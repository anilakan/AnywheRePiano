import asyncio
#from PyObjCTools import KeyValueCoding
from bleak import BleakScanner, BleakClient
# import keyboard

unique_uuid = "00002a56-0000-1000-8000-00805f9b34fb"
import signal
import sys

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

async def ble(loop):
    devices = await BleakScanner.discover()
    # remember to disconnect from BlueSee
    found_ble = False
    # for d in devices: 
    #     print(d.details)
    for d in devices: 
        if d.name == "NishBLE!":
            print(d.address)
            print(d.details)
            found_ble = True
            break
    if not found_ble:
        print("oh no")
        exit()
    address = d.address

    # make a graceful excit if you can't find nish ble
    # loop.stop()
    # while(True):
    async with BleakClient(address, loop=loop) as client:
        await client.connect()
        svcs = client.services
        while(client.is_connected):
            for service in svcs:
                # print(service)
                # print(type(service)) # i feel like there's a better way to iterate but fuck it 
                for char in service.characteristics:
                    # print(char.uuid)
                    value = await client.read_gatt_char(char.uuid)

                    print(int.from_bytes(value,byteorder='big'))
            # if(keyboard.read_key() == "q"):
            #     client.disconnect()
            #     break
        # svcs = client.services
        # for service in svcs: 
        #     for char in service.characteristics:
        #         value = await client.read_gatt_char(char.uuid)
        #         print(int.from_bytes(value, byteorder='big'))

    #loop.stop()


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
asyncio.ensure_future(ble(loop))
loop.run_forever()


# async def main():

#     # device = await BleakScanner.find_device_by_name("Happy birthday!")
 
#     # #device = await BleakScanner.find_device_by_address("31311A1E-F38C-5664-F9B3-87912D857DB6")
#     # print(device.name)
#     # print(device.details)
#     devices = await BleakScanner.discover()
#     # remember to disconnect from BlueSee
    
#     for d in devices: 
#         if d.name == "NishBLE!":
#             print(d.address)
#             print(d.details)
#             break

#     address = d.address
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     asyncio.ensure_future(ble(loop))
#     loop.run_forever()
    # async with BleakClient(address) as client:
    #     svcs = client.services

    #     for service in svcs:
    #         print(service)
    #         print(type(service)) # i feel like there's a better way to iterate but fuck it 
    #         for char in service.characteristics:
    #             print(char.uuid)
    
    #     value = await client.read_gatt_char(unique_uuid)
    #     print(int.from_bytes(value, byteorder = 'little'))
        #battery_level = await client.read_gatt_char(uuid_battery_level_characteristic)
        #print(int.from_bytes(battery_level,byteorder='big'))
# put this all into a catch and try
   # objc.listInstanceVariables("NSKVONotifying_CBPeripheral")
   
# asyncio.run(ble())
# asyncio.run(main())