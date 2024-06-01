from pathlib import Path
from random import choices
from string import hexdigits
from uuid import uuid4

from flask import Flask, jsonify, render_template, request, session
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import SystemMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

CONNECTION_STRING = "sqlite:///simple_chatbot.db"


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """
    This function retrieves the chat message history for a specific session ID.
    It uses the SQLChatMessageHistory class from the langchain_community library.
    """
    return SQLChatMessageHistory(session_id, CONNECTION_STRING)


def create_app():
    """
    This function creates a Flask application instance and configures it for the chatbot.
    """

    # Delete the database file if it exists (optional, for clean start)
    Path(CONNECTION_STRING).unlink(missing_ok=True)

    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY="".join(choices(hexdigits, k=64)),
    )

    # Initialize the OpenAI chat model (replace "gpt-4o" with your desired model)
    model = ChatOpenAI(model="gpt-4o")

    # Define the chat prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(
                content="You are a virtual assistant named 'SimpleChatBot'. You are an expert on video-games focused on point-and-click adventure games."
            ),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template(template="{input}"),
        ]
    )

    # Build the chain of processing steps for the chatbot
    chain = (
        RunnablePassthrough.assign(messages=lambda x: x["history"][-10:])
        | prompt
        | model
    )

    # Wrap the chain with message history handling
    with_message_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )

    @app.route("/")
    def index():
        """
        This function renders the main HTML template for the chatbot interface.
        It also creates a new session ID and stores it in the session.
        """
        session["id"] = str(uuid4())
        return render_template("index.html")

    @app.route("/chatbot", methods=["POST"])
    def chatbot():
        """
        This function handles incoming chat messages from the user.
        It retrieves the user's message from the request form,
        processes it through the chat chain with message history,
        and returns the chatbot's response as JSON.
        """
        response = with_message_history.invoke(
            {"input": request.form.get("message")},
            config={"configurable": {"session_id": session["id"]}},
        )
        return jsonify(message=response.content), 200

    return app
