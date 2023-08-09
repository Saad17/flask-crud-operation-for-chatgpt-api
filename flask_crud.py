from flask import Flask, request, jsonify
from helper import chatGPT
app = Flask(__name__)



# create prompt route that takes input from user and add it into prompt list
@app.route('/api/gpt/query/createprompt', methods=['POST'])
def prompt():
    if request.is_json:      
        request_data = request.get_json()
        prompt = (request_data['input'])
        response = gpt3.create_prompt(prompt)
        return jsonify(response)
    
'''
response endpoint that take prompt_index as query parameter and then pass it to 
the response_prompt function of chatGPT class
'''
@app.route('/api/chat/<string:query>', methods=['GET'])
def get_gpt_response(query):
    request_data = request.args.to_dict()
   
    prompt_index = int(request_data['prompt_index'])
    gpt_response = gpt3.response_prompt(prompt_index)

    # return the chatgpt api response against this api call
    return jsonify(gpt_response)


'''update prompt endpoint and function that takes prompt index and new prompt as query parameters and then pass it 
to update_prompt function of chatGPT class
'''
@app.route('/api/gpt/update/<int:prompt_index>/<string:new_prompt>', methods=['PUT'])
def update_user_prompt(prompt_index, new_prompt):

    prompt_index = prompt_index 
    new_prompt = new_prompt 
    response = gpt3.update_prompt(prompt_index, new_prompt)
    return jsonify(response)


'''delete prompt endpoint and function that takes prompt_index as query param and 
delete the specified index prompt from the prompt list'''

@app.route('/api/gpt/delete', methods= ['DELETE'])
def del_specific_prompt():
    request_data = request.args.to_dict()
    prompt_index = int(request_data['prompt_index'])
    response = gpt3.delete_prompt(prompt_index)
    return jsonify(response)

if __name__=='__main__':

    #openai chatgpt api key, replace it with your api key
    api_key = ''

    # create object of the chatGPT class
    gpt3 = chatGPT(api_key)

    #run flask api on localhost 
    app.run(host = '0.0.0.0', port=5000)