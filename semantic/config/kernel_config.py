from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

def get_kernel():
    kernel = Kernel()
    kernel.add_service(AzureChatCompletion())
    return kernel
