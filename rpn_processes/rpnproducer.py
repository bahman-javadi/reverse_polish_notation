import inspect
import logging
import os
import time

from rpn_processes import rpn_process

logger = logging.getLogger(__name__)


class RpnProducer(rpn_process.ProcessWithIPC):
    """
    Reads the input iterable line by line, and append the line content along with its' line number (as a tuple) to a
    queue shared with multiple consumers. There is a process_limit_size argument. The producer
    has a line counter which is equal number of processed lines. When the line counter reaches the
    process_limit_size, the process would be paused, and waits for calling resume() from the main.
    """
    def __init__(self, input_iterable, producer_queue, queue_limit, comment_identifier):
        super(RpnProducer, self).__init__()
        self._producer_queue = producer_queue
        self.set_shared_parameter('isFinished', False)
        self.set_shared_parameter('isPaused', False)
        self.set_shared_parameter('pauseReceived', False)
        self.set_shared_parameter('continueProducing', True)
        self.set_shared_parameter('queueIsFull', False)
        self.set_shared_parameter('currentLine', 0)
        self._input_iterable = input_iterable
        self._queue_limit = queue_limit
        self._comment_identifier = comment_identifier

    def run(self) -> None:
        logger.debug(f'Producer {os.getpid()} started.')

        # This is used to detect if a line is a comment
        def is_comment_line(line): return line.startswith(self._comment_identifier)

        try:
            # Read an item from the input iterable
            for string_item in self._input_iterable:

                # Check if we hit full queue
                if self.get_shared_parameter('currentLine') >= self._queue_limit:
                    logger.debug(f'Producer - Hit Full Queue, going to pause the thread')
                    # Pauses itself and wait continueProducing signal from the main thread
                    self.pause()
                    # Confirm pausing
                    self.set_shared_parameter('isPaused', True)
                    self.set_shared_parameter('queueIsFull', True)
                    while not self.get_shared_parameter('continueProducing'):
                        time.sleep(0.1)

                # Check if there is any pause command arrived?
                if self.get_shared_parameter('pauseReceived'):
                    logger.debug(f'Producer - Pause command arrived.')
                    self.set_shared_parameter('isPaused', True)
                    while not self.get_shared_parameter('continueProducing'):
                        time.sleep(0.1)

                self.set_shared_parameter('queueIsFull', False)

                string_item = string_item.strip()
                current_line = self.get_shared_parameter('currentLine')

                if not string_item:
                    logger.debug(f'Producer found an empty line {current_line}. It will be ignored !')
                elif is_comment_line(string_item):
                    logger.debug(f'Producer found commented line {current_line}. It will be ignored !')
                else:
                    # Put the read line into the queue shared by consumers
                    self._producer_queue.put((current_line, string_item))
                    logger.debug(f"Producer put one item {current_line} {string_item} to the queue.")

                self.set_shared_parameter('currentLine', current_line + 1)

            # Signaling finished
            self.set_shared_parameter('isFinished', True)
        except Exception as exc:
            self.get_exception_queue().put(exc)

        logger.debug(f"Producer {os.getpid()} finished.")

    def reset_line_counter(self):
        """
        This is used to reset counter to zero after each full queue hit
        :return: None
        """
        logger.debug(f"{inspect.currentframe().f_code.co_name}()  called.")
        self.set_shared_parameter('currentLine', 0)
        self.set_shared_parameter('queueIsFull', False)

    def is_finished(self):
        """
        Checks if the spawned process is finished or not
        :return:
        """
        return self.get_shared_parameter('isFinished')

    def hit_full_queue(self):
        """
        Checks if the queue is full or not
        :return: Boolean
        """
        val = self.get_shared_parameter('queueIsFull')
        return val

    def pause(self):
        """
        Sets the pauseReceived ti True
        :return:
        """
        logger.debug(f"{inspect.currentframe().f_code.co_name}()  called.")
        self.set_shared_parameter('continueProducing', False)
        self.set_shared_parameter('pauseReceived', True)

    def resume(self):
        """
        Continue producing input data.
        :return:
        """
        logger.debug(f"{inspect.currentframe().f_code.co_name}()  called.")
        self.set_shared_parameter('pauseReceived', False)
        self.set_shared_parameter('isPaused', False)
        self.set_shared_parameter('continueProducing', True)
