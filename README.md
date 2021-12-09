# RPN Runner
## About
The [RPN](https://en.wikipedia.org/wiki/Reverse_Polish_notation) Runner project reads data from an input file.
The input file contains RPN expressions in each line. Each line then will split via a delimiter of ','.\
  This is a sample content for a valid input data containing two RPN expressions:
 ```
 2, 3, +, 5, *  
 10, 7, 2, -, /
 ```
  RPN Runners processes the input file and generates the corresponding 
  [Infix](https://en.wikipedia.org/wiki/Infix_notation) expression with minimum parenthesis plus their evaluation.\
  The processed values then will be printed to stdout with the same order as read from the input file.
  The output of PRN runner for the previous input sample, will be:
  ```
( 2 + 3 ) * 5 = 25
10 / ( 7 - 2 ) = 2 
 ```  
**NOTE 1:** Spaces within each line will be ignored.\
**NOTE 2:** The input file might contain comments beginning with a pound sign (#). Comment lines will be ignored.\
**NOTE 3:** If for any reason, a line could not be processed, an error string starting for the corresponding line 
 will be printed in the output. The error string starts with 'ERROR'.\


## Usage
The project is implemented with Python 3.6.10, and has no third-party library dependency.\
To run the runner, simply execute the following command from the source directory:
```
python3 ./rpn_runner.py /path/to/input/file.txt
```

### Features
In implementing the runner, it is assumed that input files could be huge. Also, scalability is another concern while 
designing the architecture. To these ends, RPN Runner is implemented in a multi-threaded fashion.\
The runner spawns three types of processes:
1. RPN Producer: A single producer which reads the input file line by line, and append the line content along with its' line number 
(as a tuple) to a queue shared with multiple consumers. There is a process_limit_size option with default value of 10. 
The producer has a line counter which is equal number of processed lines. When the line counter reaches the process_limit_size, 
the process would be paused, and waits for a signal from the main thread to resume.
    ```
    python3 ./rpn_runner.py /path/to/input/file.txt --process_limit_size=100 # Sets process_limit_size to 100 lines
    ```  
2. RPN Consumer: A single or multiple consumer(s) will pop the produced tuple from the shared queue. The popped item will be then evaluated
 and the results are appended to a result queue. Each consumer has its' own result queue. The number of the consumers can
 be provided via --worker_threads_count with a default value of 2.
     ```
     python3 ./rpn_runner.py /path/to/input/file.txt --process_limit_size=100 --worker_threads_count=10 # Sets process_limit_size to 100 lines,
    and spawns 10 worker threads.
    ```
3. Main Thread: The main thread is responsible for dispatching and orchestrating consumer and producers processes. Whenever, 
process_limit_size is reached by the producer, the main threads waits until all the items in the shared queue are consumed. The 
main thread will then pause all consumer threads, and collect the processed items from them. The main thread will ,in the end,
sort the collected results according to their line number and print them out to STDOUT.   
 
 **NOTE:** Provided values for process_limit_size and worker_threads_count could have an impact on the performance. Please 
 note that having a lot of worker threads could backfire as lock contention. The max suggested value for 
 threads_count is: number of cpu cores - 2. Also, increasing process_limit_size to high numbers could cause pauses in 
 streaming the results to the output as the results are streamed in batches after reaching process_limit_size.\
 **NOTE:** there is a verbose option to print out debug logs, if needed. 
 ```
python3 ./rpn_runner.py -v
```

## Testing
The project includes unit tests written via Python uniitest. The unit tests are located in the uniitests sub-folder.
The project also has an integration test named 'test_rpn_runner.py'. The integration test runs three scenarios and 
asserts the printed results.
```
To run a unit test called test_binary_expression_tree: python3 -m unittest unittests/test_binary_expression_tree.py
```
```
To run the integration test: python3 -m unittest test_rpn_runner.py
```
