import json
import quizlet_api_wrapper


class QuizletApiUtilities:

    def get_new_set_id(json_string):
        # fetches set_id from json response of create_new_set() method from Quizlet API

        datastore = json.loads(json_string)
        return datastore['set_id']

    def get_new_term_id(json_string):
        # fetches term_id from json response of add_single_term() method from Quizlet API

        datastore = json.loads(json_string)
        return datastore['id']


class UsingQuizletApiWrapper:

    qz_api_instance = quizlet_api_wrapper.QuizletApiClass()

    # read necessary credentials from private_creds.json
    qz_api_instance.read_creds()

    # get read and write access tokens
    qz_api_instance.fetch_read_write_access_token_from_cache()

    # create new set
    list_of_definition = [('term1', 'def1'), ('term2', 'def2'), ('term3', 'def3')]
    new_set_json_string = qz_api_instance.create_new_set(term_def_list=list_of_definition)
    print(new_set_json_string)

    new_set_id = QuizletApiUtilities.get_new_set_id(new_set_json_string)  # fetch new set_id from json response

    # fetch terms from set
    print(qz_api_instance.fetch_terms_from_a_set(new_set_id))

    # fetch terms along with additional details from a set
    print(qz_api_instance.fetch_all_details_from_a_set(new_set_id))

    # add a new term to a set
    new_term_json_string = qz_api_instance.add_single_term(set_id=new_set_id, term='term4', definition='definition4')
    new_term_id = QuizletApiUtilities.get_new_term_id(new_term_json_string) # get term_id of a new term added
    print(new_term_id)

    # edit a single term
    print(qz_api_instance.edit_single_term(set_id=new_set_id, term_id=str(new_term_id)))

    # delete a single term from a set
    print(qz_api_instance.delete_single_term(set_id=new_set_id, term_id=new_term_id))  # first create a term to delete

    # fetch minimal details of a user
    print(qz_api_instance.fetch_minimal_user_details(qz_api_instance.USERNAME))

    # delete whole set
    print(qz_api_instance.delete_set(new_set_id))
    # print(x.edit_whole_set(set_id=299289740, title='My second set via api', term_def_list=list_of_definition ))
