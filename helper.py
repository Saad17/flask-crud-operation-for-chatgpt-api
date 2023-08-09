import openai
from datetime import datetime, timezone
import multiprocessing.queues as mpq
import functools
import multiprocessing as mp
import dill
from typing import Tuple, Callable, Dict, Any


class TimeoutError(Exception):

    def __init__(self, func: Callable, timeout: int):
        self.t = timeout
        self.fname = func.__name__

    def __str__(self):
            return f"function '{self.fname}' timed out after {self.t}s"


def _lemmiwinks(func: Callable, args: Tuple, kwargs: Dict[str, Any], q: mp.Queue):
    """lemmiwinks crawls into the unknown"""
    q.put(dill.loads(func)(*args, **kwargs))


def killer_call(func: Callable = None, timeout: int = 10) -> Callable:
    """
    Single function call with a timeout

    Args:
        func: the function
        timeout: The timeout in seconds
    """

    if not isinstance(timeout, int):
        raise ValueError(f'timeout needs to be an int. Got: {timeout}')

    if func is None:
        return functools.partial(killer_call, timeout=timeout)

    @functools.wraps(killer_call)
    def _inners(*args, **kwargs) -> Any:
        q_worker = mp.Queue()
        proc = mp.Process(target=_lemmiwinks, args=(dill.dumps(func), args, kwargs, q_worker))
        proc.start()
        try:
            return q_worker.get(timeout=timeout)
        except mpq.Empty:
            raise TimeoutError(func, timeout)
        finally:
            try:
                proc.terminate()
            except:
                pass
    return _inners


class chatGPT():
    def __init__(self, open_ai_api_key):
        openai.api_key = open_ai_api_key

        # self.messages define the role to the chatgpt api
        self.messages = [
            {'role': 'system', 'content':' you are a helpful AI engine'},
            {'role': 'assistant', 'content': 'Hello, what do you want to know about AI'}
        ]
        self.user_prompt = []

    # add prompt to the in-memory data structure (list)
    def create_prompt(self, prompt):
       
        self.user_prompt.append(prompt)
        return {'message': f'user input has been added successfully to the prompt list'}


    # decorator to apply timeout, if chatgpt api took so long to respond, terminate the request after specified time
    @killer_call(timeout=20)
    def response_prompt(self, prompt_index):

        # check if the prompt_index exist in a self.user_prompt list
        if 0 <= prompt_index < len(self.user_prompt):
            
            # store the prompt 
            prompt = self.user_prompt[prompt_index]

            # add the user role into self.messages list
            user_role = {'role': 'user', 'content': prompt}
            self.messages.append(user_role)

            # call chatgpt api and store the response into response variable
            response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages = self.messages
            )
            # remove the user role from the self.messages
            self.messages = [item for item in self.messages if item.get('role') != 'user']

            # return the chatgpt api response 
            return response['choices'][0]['message']['content']
        else:
            return {'message': f'user prompt_index is not exist'}
        
    #update prompt
    def update_prompt(self, prompt_index, new_prompt):
        
        # check if the prompt_index exist in a self.user_prompt list
        if 0 <= prompt_index < len(self.user_prompt):  

            # update the self.user_prompt specified index value by the new prompt  
            self.user_prompt[prompt_index] = new_prompt
            return {'message': f'user prompt has been updated successfully'}
        else:
            return {'message': f'user prompt_index is not exist'}
        
    # delete prompt 
    def delete_prompt(self, prompt_index):

        # check if the prompt_index exist in a self.user_prompt list
        if 0 <= prompt_index < len(self.user_prompt):

            # del the specified index values from the self.user_prompt
            del self.user_prompt[prompt_index]
            return {'message': f'user prompt has been deleted successfully'}
        else:
            return {'message': f'user prompt_index is not exist'}