import RPi.GPIO as gpio
import time
import LCD1602 as lcd

HTpin = 17 

gpio.setmode(gpio.BCM)
max_count = 100 

stats_sc_low = 1
stats_sc_high = 2
stats_dc_first_low = 3
stats_dc_high = 4
stats_dc_low = 5
 
def read_ht():
    gpio.setup(HTpin, gpio.OUT) 
    gpio.output(HTpin, gpio.HIGH) 
    time.sleep(0.05)
    gpio.output(HTpin, gpio.LOW)
    time.sleep(0.02)
    gpio.setup(HTpin, gpio.IN, gpio.PUD_UP)
 
    same_count = 0
    last = -1
    data = [] 
    while True: 
        curr_data = gpio.input(HTpin)
        data.append(curr_data) 
        if last != curr_data:
            same_count = 0
            last = curr_data
        else:
            same_count += 1
            if same_count > max_count:
                break
 
    stats = stats_sc_low
    lengths = [] 
    curr_lengths = 0
    for curr in data:
        curr_lengths += 1
        if stats == stats_sc_low:
           	if curr == gpio.LOW:
                    stats = stats_sc_high
        else:
            continue
        if stats == stats_sc_high:
          	if curr == gpio.HIGH:
                    stats = stats_dc_first_low
        else:
            continue
        if stats == stats_dc_first_low:
           	if curr == gpio.LOW:
                    stats = stats_dc_high
        else:
            continue
        if stats == stats_dc_high:
           	if curr == gpio.HIGH:
                    stats = stats_dc_low
                    curr_lengths = 0
        else:
             continue
        if stats == stats_dc_low:
           	if curr == gpio.LOW:
                    stats = stats_dc_high
                    lengths.append(curr_lengths)
        else:
            continue


    if len(lengths) != 40:
        #print("ERROR: Podaci nisu dobri")
        return False

    bits = []
    the_bytes = []
    byte = 0
    short_high = min(lengths)
    long_high = max(lengths)
    half = (long_high + short_high) / 2

    for length in lengths:
        bit = 0
        if length > half:
            bit = 1
        else:
            bit = 0
    bits.append(bit)
    for i in range(0, len(bits)):
        byte = byte << 1
        if bits[i]:
            byte = byte | 1
        else:
            byte = byte | 0
        if ((i+1)%8 == 0):
            the_bytes.append(byte)
            byte = 0
 
    chsuma = (the_bytes[0] + the_bytes[1] + the_bytes[2] + the_bytes[3]) & 0xFF
    if the_bytes[4] != chsuma:
        # print ("ERROR: Provera nije prosla")
        return False
 
    return the_bytes[2], the_bytes[0]
 
def lcd_show(temp, humi):
    lcd.init(0x27, 1)
    lcd.write(0, 0, f'Temperatura: {temp}')
    lcd.write(0, 1, f'Vlaznost: {humi}')
    time.sleep(2)

def main():
    while True:
        res = read_ht()
        if res:
            temp, humi = res
            print(f"Temperatur: {temp}, Vlaznost: {humi}")
            lcd_show(temp, humi)
        time.sleep(1)
 
def destroy():
    gpio.cleanup()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        destroy()