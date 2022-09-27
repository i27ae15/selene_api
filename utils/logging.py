import datetime
import inspect
import time

class Print():

    __check_variables = True

    def __init__(self, text:str, var=None, num_lines=50, al=True, num_al=1, bl=True, num_bl=1, include_time=True) -> None:

        if num_al < 1:
            num_al = 1
        
        if num_bl < 1:
            num_bl
        
        if al:
            for _ in range(0, num_al):
                print('-'*num_lines)
        
        if type(text) is list or type(text) is tuple:
            for index, t in enumerate(text):
                if var:
                    if type(var) is list or type(var) is tuple:
                        print(f'{self.get_variable_name(t)}: {var[index]}')
                    else:
                        print(f'{self.get_variable_name(t)}: {var}')
                else:
                    if self.__check_variables:
                        
                        # check if t is a variables, during the loop through we found that a 
                        # ceratin t value is not a variable we call __check_variables to be false, 
                        # since we have to assumed that all following values for t aren't going to be a variable

                        # the only thing to consider if in the case that some values are variables and others are not
                        
                        # we choose the first approach since is the most common to encounter

                        if (var_name := self.get_variable_name(t)):
                            print(f'{var_name}: {t}')
                        else:
                            print(t)
                            self.__check_variables = False
                    else:
                        print(t)
        else:
            if var:
                if text is None:
                    print(f'{self.get_variable_name(var)}: {var}')
                elif text is not None:
                    print(f'{text}: {var}')
            else:

                # even though we're calling for text, this text can be a variable, so ,
                # we need to check if it's a variable, if it is a variable, we are going 
                # to perform special treatment

                if (var_name := self.get_variable_name(text)):
                    print(f'{var_name}: {text}')
                else:
                    print(text)


        if include_time:
            print('-'*num_lines)
            print(f'runtime: {datetime.datetime.now().time()}')

        if bl:
            for _ in range(0, num_bl):
                print('-'*num_lines)


    def get_variable_name(self, var):
        callers_local_vars = inspect.currentframe().f_back.f_back.f_locals.items()
        var_name = [var_name for var_name, var_val in callers_local_vars if var_val is var]
        return var_name[0] if var_name else None


class MeassureTime():


    def __init__(self, func, parameters=dict()) -> None:
        self.func = func
        self.parameters = parameters

        start = time.time()
        func(*parameters)
        end = time.time()

        Print('time', end - start)
