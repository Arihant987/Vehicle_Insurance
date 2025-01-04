import sys
import logging

def error_message_detail(error:Exception,error_detail:sys)->str:
    '''
    Extracts detailed error message including file name,line number
    and the
    :param error: Exception
    :param error_detail: sys module to access traceback details
    :return: string
    '''

    # Extracting traceback details{Exception type,Exception message,File name,Line number} i.e. exception information
    _, _,exc_tb=error_detail.exc_info()

    file_name=exc_tb.tb_frame.f_code.co_filename
    line_number=exc_tb.tb_lineno
    error_message=f"Error occured in python script {file_name} at line number {line_number} with error message {error}"

    logging.error(error_message)

    return error_message

class MyException(Exception):
    '''
    Custom exception class for handling errors
    '''
    def __init__(self,error_message:str,error_detail:sys):
        
        super().__init__(error_message)

        self.error_message=error_message_detail(error_message,error_detail)

    def __str__(self):
        '''
        Returns the string representation of error message
        '''
        return self.error_message