import random
import rpn_runner
import unittest


class TestRpnRunner(unittest.TestCase):
    """
    This is an integration test for RPN Runner.
    Runs RPN Runner with different threads and batch sizes and asserts the results.
    To run the integration test : python3 -m unittest test_rpn_runner.py
    """

    def _execute_runner_assert_logs(self, test_input_list, expected_results_list, workers_count, comment_identifier,
                                    batch_size):
        parser = rpn_runner.get_parser()
        args = parser.parse_args(
            ['dummy_input.txt', f'--worker_threads_count={workers_count}',
             f'--comment_identifier={comment_identifier}', f'--process_limit_size={batch_size}'])
        rpn_runner.prepare_logging(verbose=False)

        with self.assertLogs(rpn_runner.logger_name, level='INFO') as context_manager:
            rpn_runner.start_main_thread(input_args=args, input_iterable=test_input_list)
            self.assertEqual(len(context_manager.output), len(expected_results_list))
            for idx in range(len(expected_results_list)):
                self.assertIn(expected_results_list[idx], context_manager.output[idx])

    def test_rpn_runner_single_line(self):
        test_input_list = ['2, 3, +, 5, *']
        test_expected_results = ['(2 + 3) * 5 = 25']
        comment_identifier = '#'
        test_batch_sizes = [1, 2, 3, 10, 100]

        # Test multiple threads from 1 to 10
        for threads in range(5):
            for batch_size in test_batch_sizes:
                print(f"Running test_rpn_runner_single_line with {threads + 1} threads. Batch Size = {batch_size}",
                      flush=True)
                self._execute_runner_assert_logs(test_input_list=test_input_list,
                                                 expected_results_list=test_expected_results,
                                                 workers_count=threads + 1,
                                                 comment_identifier=comment_identifier,
                                                 batch_size=batch_size)

    def test_rpn_runner_multi_line(self):
        test_input_list = ['#CMNT', '2, 3, +, 5, *', '#COMMENT', 'sds', '#CMNT', '10,7,2,3', '10, 7, 2, -, /', '#CMNT']
        test_expected_results = ['(2 + 3) * 5 = 25', 'ERROR', 'ERROR', '10 / (7 - 2) = 2']
        comment_identifier = '#'
        test_batch_sizes = [1, 2, 3, 10, 100]

        # Test multiple threads from 1 to 5
        for threads in range(5):
            for batch_size in test_batch_sizes:
                print(f"Running test_rpn_runner_multi_line with {threads + 1} threads. Batch Size = {batch_size}",
                      flush=True)
                self._execute_runner_assert_logs(test_input_list=test_input_list,
                                                 expected_results_list=test_expected_results,
                                                 workers_count=threads + 1,
                                                 comment_identifier=comment_identifier,
                                                 batch_size=batch_size)

    def test_rpn_runner_1000lines(self):
        test_sample_list = [
            ('#CMNT', None),
            ('2, 3, +, 5, *', '(2 + 3) * 5 = 25'),
            ('#COMMENT', None),
            ('sds', 'ERROR'),
            ('#CMNT', None),
            ('10,7,2,3', 'ERROR'),
            ('10, 7, 2, -, /', '10 / (7 - 2) = 2'),
            ('#CMNT', None)
        ]

        comment_identifier = '#'
        test_batch_sizes = [100, 1000, 5000]
        threads_list = [2, 5, 10]

        random_test_data = random.choices(test_sample_list, k=1000)
        test_input_list = [line[0] for line in random_test_data]
        test_expected_results = [line[1] for line in random_test_data if line[1] is not None]

        # Test multiple threads from 1 to 5
        for thread in threads_list:
            for batch_size in test_batch_sizes:
                print(f"Running test_rpn_runner_big_scenario with {thread} threads. Batch Size = {batch_size}",
                      flush=True)
                self._execute_runner_assert_logs(test_input_list=test_input_list,
                                                 expected_results_list=test_expected_results,
                                                 workers_count=thread,
                                                 comment_identifier=comment_identifier,
                                                 batch_size=batch_size)


if __name__ == '__main__':
    unittest.main()
