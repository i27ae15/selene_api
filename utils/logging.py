import inspect, re


class Print():
    def __init__(self, text:str=None, v=None) -> None:
        

        print('-'*50)
        
        if type(text) is list or type(text) is tuple:
            for index, t in enumerate(text):
                if v:
                    if type(v) is list or type(v) is tuple:
                        print(self.get_var_name(t) + ': ', v[index])
                    else:
                        print(self.get_var_name(t) + ': ', v)
                else:
                    print(t)
        else:
            if v:
                if text is None:
                    print(self.get_var_name(v) + ': ', v)
                elif text is not None:
                    print(text + ': ', v)
            else:
                print(text)

        print('-'*50)
        
    def gget_var_name(self, p):
        for line in inspect.getframeinfo(inspect.currentframe().f_back)[3]:
            m = re.search(r'\bgget_var_name\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)', line)
            if m:
                return m.group(1)
        return 'None'



def get_var_name(p):
        for line in inspect.getframeinfo(inspect.currentframe().f_back)[3]:
            m = re.search(r'\bget_var_name\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)', line)
            if m:
                return m.group(1)
        return 'None'
    

def second (f, s):
    get = get_var_name(f)
    Print(get, s)


    

gretting = 'Hello World!'
get_var_name(gretting)
            