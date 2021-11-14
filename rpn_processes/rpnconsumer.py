import inspect
import logging
import os
import time

from binary_expression_tree import binary_expression_tree
from rpn_processes import rpn_process

logger = logging.getLogger(__name__)


class RpnConsumer(rpn_process.ProcessWithIPC):
    """
     A single or multiple consumer(s) will pop the (line_no, line) tuple from the queue shared by producer.
     The popped item will be then evaluated and the results are appended to the result queue.
    """
    def __init__(self, producer_queue):
        super(RpnConsumer, self).__init__()
        self._binary_expression_tree = binary_expression_tree.ExpressionTree()
        self._producer_queue = producer_queue
        self.set_shared_parameter('isFinished', False)
        self.set_shared_parameter('isPaused', False)
        self.set_shared_parameter('pauseReceived', False)
        self.__result_list = self.get_result_queue()

    def run(self):
        logger.debug(f'Consumer {os.getpid()} started.')
        try:
            while True:
                # Check if there is any pause command.
                if self.get_shared_parameter('pauseReceived'):
                    # Confirm pausing
                    self.set_shared_parameter('isPaused', True)
                    # Wait until pauseReceived is reset
                    while self.get_shared_parameter('pauseReceived'):
                        time.sleep(0.1)

                try:
                    # Pop an item from the queue. Timeout is set to 0.1 second.
                    item = self._producer_queue.get(timeout=0.1)
                    logger.debug(f"Consumer {os.getpid()} took item '{item}' from the queue.")
                except:
                    # An exception caught. Check if producer is finished?
                    if self.get_shared_parameter('isFinished'):
                        logger.debug(f"Consumer {os.getpid()} detected finished producer event. Returning.")
                        self.set_shared_parameter('isPaused', True)
                        return
                    else:
                        # _producer_queue couldn't pop any item probably because of empty shared queue
                        continue

                line_no, current_postfix = item
                try:
                    # Process the input item and generate the corresponding result
                    current_result, current_infix = self._binary_expression_tree.process(current_postfix)
                    result = (line_no, f"{current_infix} = {int(current_result)}")
                except Exception as exc:
                    result = (line_no, f"ERROR- Could not parse the input line {line_no} '{current_postfix}. "
                                       f"Details: {exc}")

                # This needs to be set after each item pop as we're using joinableQueue.
                self._producer_queue.task_done()
                # Put the result in the result queue
                self._result_list.put(result)
                logger.debug(f"Consumer {os.getpid()} put result '{result}' to the result list.")
        except Exception as exc:
            # Any exception caught will be put into the exception queue to be handled by the main thread.
            self.get_exception_queue().put(exc)

        logger.debug(f"Consumer {os.getpid()} finished.")

    def get_results(self):
        logger.debug(f"{inspect.currentframe().f_code.co_name}()  called.")
        self.set_shared_parameter('pauseReceived', True)
        # Wait for pause to be confirmed
        while not self.get_shared_parameter('isPaused'):
            time.sleep(0.1)

        return_list = []
        while self._result_list.qsize() != 0:
            return_list.append(self._result_list.get())

        # Continue consuming from the shared input queue
        self.set_shared_parameter('pauseReceived', False)
        self.set_shared_parameter('isPaused', False)
        logger.debug(f"Returning results : {return_list}")

        return return_list

    def set_finished_flag(self):
        logger.debug(f"{inspect.currentframe().f_code.co_name}()  called.")
        self.set_shared_parameter('isFinished', True)
