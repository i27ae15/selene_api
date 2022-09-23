class Print():
    def __init__(self, text:str, variable=None) -> None:

        print('-'*50)
        
        if type(text) == list or type(text) == tuple:
            for index, t in enumerate(text):
                if variable:
                    if type(variable) == list or type(variable) == tuple:
                        print(t + ': ', variable[index])
                    else:
                        print(t + ': ', variable)
                else:
                    print(t)
        else:
            if variable:
                print(text + ': ', variable)
            else:
                print(text)

        print('-'*50)