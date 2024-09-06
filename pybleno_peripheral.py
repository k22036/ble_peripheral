import time
from pybleno import *

bleno = Bleno()

APPROACH_SERVICE_UUID = 'ABCABC30-8883-49A8-8BDB-42BC1A7107F4'
APPROACH_CHARACTERISTIC_UUID = 'CCCC5077-201F-44EB-82E8-10CC02AD8CE1'


class ApproachCharacteristic(Characteristic):

    def __init__(self):
        Characteristic.__init__(self, {
            'uuid': APPROACH_CHARACTERISTIC_UUID,
            'properties': ['write', 'read', 'notify'],
            'value': None
        })

        self._value = str(0).encode()
        self._updateValueCallback = None

    def onWriteRequest(self, data, offset, withoutResponse, callback):
        # バイトデータを文字列に変換（デコード）
        received_str = data.decode('utf-8', errors='replace')

        print(
            f'ApproachCharacteristic - onWriteRequest: value = {received_str}')

        if withoutResponse:
            # クライアントはレスポンスを期待していないので、何もしない
            print("Write request without response")
        else:
            # クライアントがレスポンスを期待している場合は、正常終了を通知
            callback(Characteristic.RESULT_SUCCESS)

    def onReadRequest(self, offset, callback):
        print('ApproachCharacteristic - onReadRequest')
        callback(result=Characteristic.RESULT_SUCCESS,
                 data="Hello World".encode())

    def onSubscribe(self, maxValueSize, updateValueCallback):
        print('ApproachCharacteristic - onSubscribe')

        self._updateValueCallback = updateValueCallback

    def onUnsubscribe(self):
        print('ApproachCharacteristic - onUnsubscribe')

        self._updateValueCallback = None


def onStateChange(state):
    print('on -> stateChange: ' + state)

    if (state == 'poweredOn'):
        bleno.startAdvertising(name='Approach', service_uuids=[
                               APPROACH_SERVICE_UUID])
    else:
        bleno.stopAdvertising()


bleno.on('stateChange', onStateChange)

approachCharacteristic = ApproachCharacteristic()


def onAdvertisingStart(error):
    print('on -> advertisingStart: ' +
          ('error ' + error if error else 'success'))

    if not error:
        bleno.setServices([
            BlenoPrimaryService({
                'uuid': APPROACH_SERVICE_UUID,
                'characteristics': [
                    approachCharacteristic
                ]
            })
        ])


bleno.on('advertisingStart', onAdvertisingStart)

bleno.start()


counter = 0


def task():
    global counter
    counter += 1
    approachCharacteristic._value = str(counter).encode()
    if approachCharacteristic._updateValueCallback:

        print('Sending notification with value : ' +
              str(approachCharacteristic._value))

        notificationBytes = str(approachCharacteristic._value).encode()
        approachCharacteristic._updateValueCallback(data=notificationBytes)


while True:
    task()
    time.sleep(1)
