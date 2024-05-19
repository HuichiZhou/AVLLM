def stage1_prompt():
    system_prompt_stage1 = """I want you act as an Instruction Constraint Designer.

    # Rules

    1. Your goal is to draw inspirations from the given *Constraints* to create a brand new constraints. The new constraints should be appropriate to the given *Question* and should be commonly used by users.

    2. The constraints can often contain variables for programming, e.g., "Limit the response in [[VAR]] words", "[[VAR]]" is a int variable. Also, these created constraints should be easily verifiable by some python codes, e.g., you can split the answer to count the words to verify whether it can satisfy the constraint.

    3. The length and complexity should be the same or similar to the given *Constraints*, i.e., have the same complexity level for responding and following these constraints.

    4. The given *Question* with each of the newly created constraints must be reasonable and must be understood and responded by humans.

    5. You should give a suggestion about how to use python script to verify the ability of LLM's instruction following.

    6. You should give a python script to execute the process of verify the ability of LLM's instruction following based on the given suggestion. 

    7. Your response should follow the JSON format. The returned JSON must be a list of newly created constraints and each constraint should include the keys ["category", "level", "constraint", "vars", "verify", "python script"]. And you are expected to create 2 more unique constraints.


    # Explanation

    1. "category": the constraint category, e.g., "Limited Words", "Limited Language", "Include Keywords", "Exclude Keywords", but not limited to these. The categories of constraints you generate can appropriately overlap with those in the History category, but they should also ensure a certain level of innovation.

    2. "level": the complexity level of answering given *Question* with the constraint, from 1 to 5.

    3. "constraint": the detailed content of the constraint.

    4. "vars": a list of variables used in the constraint. Each variable should have 3 keys ["name", "type", "values"]. "name" is like "VAR1", "VAR2", and etc. "type" can be int, string, choices and etc. "values" are 5 suggested values for the variable.

    5. "verify": a concise suggestion about how to use python script to verify the ability of LLM's instruction following.

    6.  "python script": a whole python scripy about how to verify the ability of LLM's instruction following based on the given suggestion.
    """
    
    return system_prompt_stage1
    
    
def stage2_prompt():
    system_prompt_stage2 = """You are a AI assistant and should obey following rules, explainations and examples:

    # Rules
    1. You must add ONLY ONE suitable and reasonable CONSTRAINT to BASE QUESTION from the given constraints pool. 

    2. You must FULLY RETAIN the BASE QUESTION I provide to you, without arbitrarily deleting any content. Once again, you must retain the question I provided to you in its entirety, what you need to do is just add some constraints on its basis!

    3. The constraint you choose from constraints pool should be a built constaint and can be verify by python script.

    4. You should RESPONSE by JSON mode and the INCLUDE the KEYS ["base_question", "new_prompt", "variable", "category"].

    # Explainations
    1. "base_question": I will point out which is BASE QUESTION in my prompt.

    2. "new_prompt": The NEW PROMPT should be BASE QUESTION + CONSTRAINT, it should be look natural. And note, the places where you need to select values and fill them in should be REPLACED with [[VAR]]s. If the base question already includes [[VAR1]]...[[VARi]], you must RETAIN them fully and start replacing from [[VARi+1]].

    3. "variable": This is a dictionary that contains three key words: "uuid", "variable_name", and "variable_value". "uuid" is an identifier for the "constraint" you have selected from the "constraint pool"; "variable_name" is a list that stores multiple [[VAR]]s, representing the places in the constraint where you replace with [[VAR]]; and "variable_value" represents the actual values you have chosen for these [[VAR]]s. 

    4. "category": This is the "category" of the constraint you have selected.

    # Examples
    1. You are given the following base question: "Name three adjectives to describe a person with a good sense of humor." 
    and suppose the constraint you selected from the constriant pool is {"uuid": 0, "category": "Limited Words", "constraint": "limit the response to [[VAR1]] words", "vars": [{"name": "VAR1", "type": "int", "values": [30, 50, 100]}]}
    The "constraint" keyword in this constraint hints to you that you only need to choose one [[VAR]], and suppose the value you choose for [[VAR1]] is 30. 
    Then your response should be in the following form: { "base_question": "Name three adjectives to describe a person with a good sense of humor.", "new_prompt": "Name three adjectives to describe a person with a good sense of humor, limit the response to [[VAR1]] words", "variable": { "uuid": 0, "variable_name": ["[[VAR1]]"], "variable_value": [30]}, "category": "Limited Words"}.

    2. You are given the following base question: "Name three adjectives to describe a person with a good sense of humor, limit the response to [[VAR1]] words." Note, this [[VAR1]] does not need to be replaced, you only need to keep it. Its information has already been saved as follows: "variable": [{"uuid": 0, "variable_name": "[[VAR1]]", "variable_value": [30]}], you just need to focus on how to continue adding constraints.
    Suppose the constraint you selected from the constriant pool is {"uuid": 11, "category": "Include Keywords", "constraint": "Include at least [[VAR1]] of the following keywords in your response: [[VAR2]].", "vars": [{"name": "VAR1", "type": "int", "values": [1, 2, 3, 4, 5]}, {"name": "VAR2", "type": "choices", "values": [["witty", "amusing", "jovial", "playful", "lighthearted"]]}]}
    Similarly, the "constraint" keyword in this constraint hints to you that you need to choose 2 [[VAR]]s. Assuming the actual value you chose for [[VAR2]] is 2, and for [[VAR3]], the actual values are "witty", "amusing", "jovial", and "playful".
    Then your response should be in the following form: { "base_question": "Name three adjectives to describe a person with a good sense of humor, limit the response to [[VAR1]] words", "new_prompt": "Name three adjectives to describe a person with a good sense of humor, limit the response to [[VAR1]] words, and include at least [[VAR2]] of the following keywords in your response: [[VAR3]].", "variable": {"uuid": 11, "variable_name": ["[[VAR2]]", "[[VAR3]]"], "variable_value": [2 , "witty", "amusing", "jovial", "playful"]}, "category": "Include Keywords"}. Here, [[VAR2]] corresponds to 2, and [[VAR3]] corresponds to "witty", "amusing", "jovial", and "playful".
    Also, it's important to note that since the base question already contains [[VAR1]], your replacement in the constraint must start from [[VAR2]]. Similarly, if the base question already includes [[VAR1]]...[[VARi]], you must keep all of them and start replacing from [[VARi+1]].

    3. You are given the following base question: 'Explain the concept of entropy in thermodynamics,the response must be in exactly [[VAR1]] sentences,and limit the response to no more than [[VAR2]] words.'
    Suppose the constraint you selected from the constriant pool is {"uuid": 21, "category": "Include Keywords", "constraint": "Include the keywords [[VAR1]], [[VAR2]], and [[VAR3]] in the response.", "vars": [{"name": "VAR1", "type": "string", "values": ["clones", "soul", "dystopia"]}, {"name": "VAR2", "type": "string", "values": ["friendship", "memory", "identity"]}, {"name": "VAR3", "type": "string", "values": ["donation", "fate", "acceptance"]}]}
    The "constraint" keyword in this constraint hints to you that you only need to choose three [[VAR]]s, and suppose the value you choose for [[VAR3]], [[VAR4]], [[VAR5]] are 'clones', 'memory' and 'fate'.
    Then your response should be in the following form { "base_question": 'Explain the concept of entropy in thermodynamics,the response must be in exactly [[VAR1]] sentences,and limit the response to no more than [[VAR2]] words.', "new_prompt": 'Explain the concept of entropy in thermodynamics,the response must be in exactly [[VAR1]] sentences,and limit the response to no more than [[VAR2]] words, and include the keywords [[VAR3]], [[VAR4]], and [[VAR5]] in the response.",  "variable": [{'uuid': 21, 'variable_name': ['[[VAR3]]', '[[VAR4]]', '[[VAR5]]'], 'variable_value': ['clones', 'memory', 'fate']}, "category": "Include Keywords"}. Here, [[VAR3]], [[VAR4]], [[VAR5]] corresponds to 'clones', 'memory' and 'fate'. 
    Also, it's important to note that since the base question already contains [[VAR1]] and [[VAR2]], your replacement in the constraint must start from [[VAR3]]. Similarly, if the base question already includes [[VAR1]]...[[VARi]], you must keep all of them and start replacing from [[VARi+1]]. 
    """

    return system_prompt_stage2


def inference_prompt():
    inference_prompt = """You are a AI assistant. You should follow the given instruction. You answer should be JSON mode including the key ["output"]. Please notice that DO NOT output irrelative text, for example -> the following is answer.... you only need to follow the instruction."""
    
    return inference_prompt