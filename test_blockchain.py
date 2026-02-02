from blockchain.contract_config import contract

result = contract.functions.verifyAudio("fairy-lullaby").call()
print(result)
