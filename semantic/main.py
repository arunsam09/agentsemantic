import asyncio
from agents.reviewer_wrapper import create_reviewer_agent
from semantic_kernel import Kernel
from semantic_kernel.agents import AgentGroupChat
from semantic_kernel.agents.strategies import KernelFunctionSelectionStrategy, KernelFunctionTerminationStrategy
from semantic_kernel.contents import ChatHistoryTruncationReducer
from semantic_kernel.functions import KernelFunctionFromPrompt
from config.kernel_config import get_kernel

REVIEWER_NAME = "Reviewer"
WRITER_NAME = "Writer"

async def main():
    kernel = get_kernel()

    reviewer_agent = create_reviewer_agent()

    writer_agent = ...  # You can plug in ChatCompletionAgent if needed

    selection_function = KernelFunctionFromPrompt(
        function_name="selection",
        prompt=f"""Examine the RESPONSE and choose the next participant:
{{{{$lastmessage}}}}"""
    )

    termination_function = KernelFunctionFromPrompt(
        function_name="termination",
        prompt=f"""If RESPONSE is satisfactory, respond with 'yes':
{{{{$lastmessage}}}}"""
    )

    chat = AgentGroupChat(
        agents=[reviewer_agent],
        selection_strategy=KernelFunctionSelectionStrategy(
            initial_agent=reviewer_agent,
            function=selection_function,
            kernel=kernel,
            result_parser=lambda result: str(result.value[0]).strip() if result.value[0] else REVIEWER_NAME,
            history_variable_name="lastmessage",
            history_reducer=ChatHistoryTruncationReducer(target_count=1),
        ),
        termination_strategy=KernelFunctionTerminationStrategy(
            agents=[reviewer_agent],
            function=termination_function,
            kernel=kernel,
            result_parser=lambda result: "yes" in str(result.value[0]).lower(),
            history_variable_name="lastmessage",
            maximum_iterations=10,
            history_reducer=ChatHistoryTruncationReducer(target_count=1),
        )
    )

    print("Ready! Type your input, or 'exit' to quit.")
    while True:
        user_input = input("User > ")
        if user_input.lower() == "exit":
            break
        await chat.add_chat_message(message=user_input)
        async for response in chat.invoke():
            print(f"#{response.name}:
{response.content}")

if __name__ == "__main__":
    asyncio.run(main())
