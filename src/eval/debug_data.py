from src.database.firestore import get_client

def get_eval_inputs():
    return get_client().get_all('AI_Eval_Inputs')

def get_eval_results():
    return get_client().get_all('Eval_Results')
