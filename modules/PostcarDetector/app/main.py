# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

try:
    import ptvsd
    __myDebug__ = True 
    ptvsd.enable_attach(('0.0.0.0',  5679))
    print("Debugging enabled in Postcardetector")
    #ptvsd.wait_for_attach()
except ImportError:
    __myDebug__ = False
    print("no debugging")

import time
import os
import sys
import asyncio
import json
from six.moves import input
import threading
from azure.iot.device.aio import IoTHubModuleClient

async def main():
    ptvsd.break_into_debugger()
    
    try:
        if not sys.version >= "3.5.3":
            raise Exception( "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version )
        print ( "IoT Hub Client for Python" )

        # The client object is used to interact with your Azure IoT hub.
        module_client = IoTHubModuleClient.create_from_edge_environment()

        # connect the client.
        await module_client.connect()

        # define behavior for receiving an input message on input1
        async def input1_listener(module_client):
            while True:
                input_message = await module_client.receive_message_on_input("input1")  # blocking call
                print("the data in the message received on input1 was ")
                ptvsd.break_into_debugger()
                message = json.loads(input_message.data)
                print(f'Class: {message["class"]}')
                print("custom properties are")
                print(input_message.custom_properties)
                print("forwarding mesage to output1")
                await module_client.send_message_to_output(input_message, "output1")

        # define behavior for halting the application
        def stdin_listener():
            while True:
                time.sleep(10)

        # Schedule task for C2D Listener
        listeners = asyncio.gather(input1_listener(module_client))

        # Run the stdin listener in the event loop
        loop = asyncio.get_event_loop()
        user_finished = loop.run_in_executor(None, stdin_listener)

        # Wait for user to indicate they are done listening for messages
        await user_finished

        # Cancel listening
        listeners.cancel()

        # Finally, disconnect
        await module_client.disconnect()

    except Exception as e:
        print ( "Unexpected error %s " % e )
        raise

if __name__ == "__main__":
    print("Main function called")
    ptvsd.break_into_debugger()
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()

    # If using Python 3.7 or above, you can use following code instead:
    # asyncio.run(main())