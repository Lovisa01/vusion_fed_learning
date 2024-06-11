from LLMEndpoint import ChatGPTEndpoint

if __name__ == "__main__":
    # Define the prompt_dict according to the required structure
    prompt_dict = {
        "systemRole": "You're a linux terminal that needs to provide ",
        "user": "Linux developer",
        "context": "Files should be based on bread bakery",
        "message": "can you create the code to create a folder structure for a bakery. Guess what that should look like. Task: provide a json of the code with the files. JSON: [{'Content_Type':'code  for creating File,folder,package etc...','Contents':' code if file then it should be file contents, if folder should be folder name'},{'Content_Type':'File,folder,package etc...','Contents':'if file then it should be file contents, if folder should be folder name'}]",
        "model" : "gpt-3.5-turbo",
        "response_format" : "json_object"
    }
    
    # Create an instance of ChatGPTEndpoint
    endpoint = ChatGPTEndpoint()
    
    # Get the response from the ChatGPT endpoint
    response = endpoint.ask(prompt_dict)
    
    if response:
        print("ChatGPT Response:", response)
    else:
        print("Failed to get response from ChatGPT.")
