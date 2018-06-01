# QuizletApiPythonWrapper
---

[Quizlet API](https://quizlet.com/api/2.0/docs) lets you create, search and modify flashcard sets and classes, and much more in our own application. QuizletApiPythonWrapper acts a wrapper around Quizlet API using Python as binding.

# How to get started?

1.   Install all the necessary packages from **requirement.txt** file.

2.  Visit [Quizlet API Dashboard](https://quizlet.com/api-dashboard) : Obtain your **client_id**, **secret_key**. Also mention your **application url** at which quizlet will redirect to.

3.  Fill all necessary details in **private_creds.json** 

    Required fields in **private_creds.json**: 

    | FIELD | VALUE |
    | ------ | ------ |
    | CLIENT_ID | Refer : [Quizlet API     Dashboard](https://quizlet.com/api-dashboard) |
    | SECRET_KEY | Refer : [Quizlet API Dashboard](https://quizlet.com/api-dashboard)  |
    | REDIRECT_URI | Refer : [Quizlet API Dashboard](https://quizlet.com/api-dashboard ) |
    | USERNAME | Any quizlet username |
    | PASSWORD | Password for above username |

4. **First time run guide** : When running for the first time, make sure you first call `read_creds()` followed by `fetch_read_write_access_token_from_cache()` so that all the necessary access token are in place for future calls with quizlet api.
