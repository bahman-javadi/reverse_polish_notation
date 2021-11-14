import itertools
import logging
import multiprocessing as mp
import sys
import time
from collections.abc import Iterable

from customized_parser import customized_parser
from rpn_processes import rpnproducer, rpnconsumer

logger_name = "RPN_Runner"
logger = logging.getLogger(logger_name)


def get_parser():
    """
    Utility function to get the parser with required arguments.
    :return: parser with required arguments
    """
    prn_calc_parser = customized_parser.CustomizedParser(prog='prn_calculator',
                                                         description='Calculates Polish Reverse Notion(PRN) for an '
                                                                     'input file.')
    prn_calc_parser.add_argument('input_file', help='Input File')
    prn_calc_parser.add_argument('--worker_threads_count',
                                 help="Number of worker threads (default = 2).",
                                 default=2)

    prn_calc_parser.add_argument('--process_limit_size',
                                 help="Sets the number of lines processed in batch (default = 10).",
                                 default=10)

    prn_calc_parser.add_argument('-v', '--verbose', help='activates debugging logs', action='store_true')

    prn_calc_parser.add_argument('--comment_identifier',
                                 help="Overrides the default comment identifier (default = pound sign(#)).",
                                 default='#')

    return prn_calc_parser


def start_main_thread(input_args, input_iterable):
    """
    Starts the main thread. The main thread is responsible for dispatching and orchestrating consumer and producers
    processes. Whenever, process_limit_size is reached by the producer, the main threads waits until all the items in
    the shared queue are consumed. The main thread will then pause all consumer threads, and collect the processed
    items from them. The main thread will ,in the end, sort the collected results according to their line number and
    print them out to STDOUT.

    :param input_args:  Arguments passed from the command line
    :param input_iterable: any iterable containing the input data
    :return:
    """
    if not hasattr(input_args, 'process_limit_size') or (int(input_args.process_limit_size) < 1):
        logger.error(f"process_limit_size argument must be a positive number.")
        sys.exit(-1)
    if not hasattr(input_args, 'worker_threads_count') or (int(input_args.worker_threads_count) < 1):
        logger.error(f"worker_threads_count argument must be a positive number.")
        sys.exit(-1)

    queue_limit = int(input_args.process_limit_size)
    worker_threads = int(input_args.worker_threads_count)

    comment_string = input_args.comment_identifier
    logger.debug(f"Number of worker threads is set to {worker_threads}.")

    if not isinstance(input_iterable, Iterable):
        raise Exception("input_iterable must be iterable.")

    input_rpn_queue = mp.JoinableQueue()
    pool_consumers = []
    producer_process = None

    try:
        # Instantiates a RpnProducer and start it. There should be only a single instance of the producer. A single
        # producer reads the input iterable line by line, and append the line content along with its' line number (as
        # a tuple) to a queue shared with multiple consumers.
        producer_process = rpnproducer.RpnProducer(input_iterable, input_rpn_queue, int(queue_limit), comment_string)
        producer_process.start()

        # Instantiates a number of worker threads and starts them.
        # Each will pop the produced tuple from the shared queue. The popped item will be then evaluated
        #  and the results are appended to a result queue.
        for i in range(int(worker_threads)):
            consumer_proc = rpnconsumer.RpnConsumer(input_rpn_queue)
            consumer_proc.start()
            pool_consumers.append(consumer_proc)

        while True:

            # Check if any exception caught by the producer
            if not producer_process.get_exception_queue().empty():
                logger.error(f"Detected an exception in the producer thread. Details : "
                             f"{producer_process.get_exception_queue().get()}")
                break

            # Check if any exception caught by the consumers
            consumer_exceptions = [consumer.get_exception_queue() for consumer in pool_consumers]
            if not consumer_exceptions:
                logger.error(f"Detected exception(s) in the consumer threads. Details : "
                             f"{consumer_exceptions}")

            # If producer hit full queue or it's finished
            if producer_process.hit_full_queue() or producer_process.is_finished():
                logger.debug("Detected full producer queue or finished producer")
                # Waiting until all of the items in queue are popped by consumers
                while not input_rpn_queue.empty():
                    logger.debug("Waiting for queue items to be processed.")
                    time.sleep(0.1)

                # Each consumer has its' own result queue. Here, the producer and consumers are already paused.
                # We collect the results from different worker threads and reorder them according to line numbers
                collected_results = [consumer.get_results() for consumer in pool_consumers]
                # Flatten the results. The result is now  a [[res1], [res2], ...]
                collected_results = [item for sublist in collected_results for item in sublist]
                logger.debug(f"Collected results = {collected_results}, now sorting the outputs by line number.")
                iters = sorted(itertools.chain(collected_results), key=lambda results: results[0])

                # If producer is not finished, resets its' line counter to zero and resume putting items into the queue
                if not producer_process.is_finished():
                    producer_process.resume()
                    producer_process.reset_line_counter()

                # printing the sorted results to the output
                for result in iters:
                    logger.debug(f'line {result[0]}:')
                    logger.info(result[1])

                if producer_process.is_finished():
                    break

    except KeyboardInterrupt:
        logger.info("Keyboard Interrupt received in the main thread.")
    except Exception as exc_main:
        logger.info(f"Exception caught in the main thread . Details: {exc_main}")

    logger.debug("Cleanup ...")
    logger.debug("Waiting for producer process to join.")
    if producer_process:
        producer_process.join()

    logger.debug("Sending finish signal to consumers.")
    for consumer in pool_consumers:
        consumer.set_finished_flag()

    logger.debug("Waiting for consumer processes to join.")
    for consumer in pool_consumers:
        consumer.join()

    logger.debug("Waiting for the joinable queue to join.")
    input_rpn_queue.join()


def prepare_logging(verbose=False):
    """
    Prepares logging module for the project
    :param verbose: if True, will print set the debug level to DEBUG.
    :return: None
    """
    logger_level = logging.DEBUG if verbose else logging.INFO
    log_format = '%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s' if verbose else '%(message)s'

    # Configuring the root logger
    logging.basicConfig(format=log_format, level=logger_level)
    logger.propagate = False
    logger.setLevel(logger_level)
    handler = logging.StreamHandler()
    handler.setLevel(logger_level)
    formatter = logging.Formatter(log_format)

    handler.setFormatter(formatter)
    logger.addHandler(handler)


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args(sys.argv[1:])
    prepare_logging(args.verbose)

    try:
        with open(args.input_file, 'r') as input_file:
            start_main_thread(args, input_file)
    except IOError as os_exc:
        logger.error(f"Exception caught while opening '{args.input_file}'. Details: {os_exc}")
        sys.exit(-1)
    except Exception as exc:
        logger.error(f"Exception caught in the main thread. Details: {exc}")
