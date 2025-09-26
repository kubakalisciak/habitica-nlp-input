# Habitica FastAdd with MacroDroid

Using the FastAdd API via Android's MacroDroid is a very straightforward task. However, setup might not be as trivial.

## Setup Instructions

1. **Install MacroDroid**: Install the app from the Play Store.

2. **Create a new macro**: After opening the app, click on `Add Macro` in the top left.

3. **Add a trigger**: In the `Triggers` tab, click the plus icon, then search for `Widget Button`. Then, select `Custom` and set up the widget to your liking.

4. **Add first action**: In the `Actions` tab, click the plus icon and select `Set Variable`. Set the variable name to `task_text` and choose `User Prompt` as the value. This will ask for input when the macro runs.

5. **Add HTTP request action**: Add another action by clicking the plus icon and selecting `HTTP Request`. Choose `POST` method and enter your FastAdd API endpoint URL (`habitica-fastadd.onrender.com/add_task`). Configure the request body (in the `Content Body`) as follows: 
    1. **Content type**: `application/json`
    2. **Content body**: set it to `text`, and in the input box write:
    ```json
    {
        'user_id': YOUR_HABITICA_USER_ID,
        'api_token': YOUR_HABITICA_API_TOKEN,
        'text': '{lv=task_text}',
    }

6. **Add cleanup action**: Add a final `Set Variable` action to clear the task_text variable by setting it to empty text.

7. **Name your macro**: Give your macro a descriptive name like "Habitica FastAdd" or similar.

8. **Save the macro**: Tap the checkmark or save button to create the macro.

9. **Add widget to home screen**: Go to your Android home screen, long-press on empty space, select "Widgets", find your MacroDroid widget, and place it on your home screen. It should now trigger your Habitica FastAdd macro when tapped.

## Usage

The widget will now allow you to quickly add tasks to Habitica by tapping it, entering your task description, and having it automatically submitted via the API.