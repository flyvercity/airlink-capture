import logging as lg
import traceback
import subprocess
import asyncio


async def wait_10s():
    for i in range(10):
        lg.info(f'Waiting {10 - i} seconds')
        await asyncio.sleep(1)


def send_command(at_command):
    return '#MONI: Test PLMN 1-1 NR_BAND:79 NR_BW:100 NR_ULBW:100 NR_CH:723360 NR_ULCH:723360 NR_PWR:-60dbm NR_RSRP:-71 NR_RSRQ:-10 NR_PCI:11 NR_SINR:56 NR_STATE:2 NR_TXPWR:239 NR_DLMOD:1 NR_ULMOD:0'
    response = subprocess.run(
        [
            'mmcli',
            '-m', '0',
            '--command', at_command

        ],
        capture_output=True
    )

    answer = response.stdout.decode('utf-8')
    print('Raw response:', answer)
    return answer


async def run(log):
    while True:
        try:
            lg.debug('Entering the cycle')
            while True:
                lg.debug('Signal quality query')
                moni_string = send_command('AT#MONI')
                lg.info('Signal quality:', moni_string)
                log.write(moni_string)
                await asyncio.sleep(1)

        except KeyboardInterrupt:
            return

        except Exception as exc:
            traceback.print_exc()
            print('There was error', exc)
            await wait_10s()


async def main():
    with open('signal.txt', 'at') as log:
        await run(log)


if __name__ == '__main__':
    asyncio.run(main())
