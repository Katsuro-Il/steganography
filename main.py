import numpy as np  # pip
from PIL import Image  # pip
from random import choice


sign = '$=(^.^)=$'  # Сигнатура окончания сообщения


# Записывает бит данных data в младший разряд байта byte
def EncodeByteLSB(byte, data):
    return int('{:08b}'.format(byte)[:-1] + data, 2)


# Кодирует бит данных data в младшый разряд байта byte.
# byte остаётся неизменным, если его младшый разряд совпадает с data,
# и величивается или уменьшается (решение принимается случайно) на 1 в ином случае
def EncodeBytePM1(byte, data):
    if (byte % 2 == 0 and data == '1') or (byte % 2 == 1 and data == '0'):
        if byte < 1:
            byte += 1  # можно только увеличивать
        elif byte > 254:
            byte -= 1  # можно только уменьшать
        else:
            byte += choice((-1, 1))
    return byte


# Кодирует бит данных b в байт c методом Модуляции индекса квантования (QIM или МИК)
def EncodeByteQIM(c, b, q):  # q - Шаг квантования, всегда чётный
    c = q * (c // q) + q * int(b) // 2
    return c if c < 256 else 255


# Кодирует сообщение message в изображение, взятое по пути source, и сохраняет
# изменённое изображение по пути destination. Метод кодирования определется параметром
# tech: LSB, PM1 или QIM (последний метод требует опциональный параметр q - шаг квантования).
def EncodeMessage(source, message, destination, tech, q=0):
    img = Image.open(source, 'r')
    # Создаём одномерный масссив, содержащий по три элемента (RGB) для каждого пикселя
    array = np.array(list(img.getdata()))
    # Ширина и высота изображения потребуются для пересохранени его в файл
    width, height = img.size

    # Определем формат внутреннего представления изоражения
    if img.mode == 'RGB':
        n = 3
    elif img.mode == 'RGBA':
        n = 4
    else:
        print('<Неподдерживаемый формат>')
        return -1

    total_pixels = array.size // n

    # Добавляем к сообщению сигнатуру конца сообщения и интерпретируем всё как текст в UTF-8
    message_bytes = bytes(message + sign, 'UTF-8')
    # Представим сообщение как строку последовательных '0' и '1' (битов)
    b_message = ''.join(['{:08b}'.format(x) for x in message_bytes])
    # Количество пикселей, необходимых для хранения сообщения
    req_pixels = len(b_message) // 3 + 1

    if req_pixels > total_pixels:
        print('<Необходимо изображение большего размера>')
    else:
        for p in range(req_pixels):  # Выбираем очередной пиксель для кодирования в него трёх битов сообщения
            for color in range(0, 3):  # Кодируем по 1 биту в R, G и B
                index = p * 3 + color  # индекс кодируемого бита сообщения
                # Длина сообщения кратна 8 битам, а количество бит в картинке - 3; проверем, что сообщение не кончилось
                if index < len(b_message):
                    # Кодирум очередной бит сообщения в байт изображения выбранным методом
                    if tech == 'LSB':
                        array[p][color] = EncodeByteLSB(array[p][color], b_message[index])
                    elif tech == 'PM1':
                        array[p][color] = EncodeBytePM1(array[p][color], b_message[index])
                    elif tech == 'QIM':
                        array[p][color] = EncodeByteQIM(array[p][color], b_message[index], q)
                    else:
                        print('<Неизвестнаый метод кодирования - ' + tech + '>')
                        return

        # Сделаем формат массива пригодным для сохранения в виде изображения
        array = array.reshape(height, width, n)
        enc_img = Image.fromarray(array.astype('uint8'), img.mode)
        enc_img.save(destination)
        print('<Сообщение успешно скрыто в изображении>')


# Ищет в изображении по пути source сообщение, закодирование известным методом, и возвращает его.
def DecodeMessage(source, tech, q=0):
    img = Image.open(source, 'r')
    array = np.array(list(img.getdata()))

    if img.mode == 'RGB':
        n = 3
    elif img.mode == 'RGBA':
        n = 4
    else:
        return '<Неподдерживаемый формат>'

    total_pixels = array.size // n

    # Приведём сигнатуру конца сообщение к последовательности '0' и '1' (битов)
    signbit = ''.join(['{:08b}'.format(x) for x in bytes(sign, 'UTF-8')])
    # Строка считанных из изображения скрытых (закодированных) битов (также в виде '0' и '1')
    hidden_bits = ''
    # Последовательно анализируем пиксели изображения
    for p in range(total_pixels):
        # В каждом пикселе 3 цвета, в каждом цвете - 1 бит сообщения
        for color in range(0, 3):
            c = array[p][color]

            # Только для метода QIM ##############################################
            if tech == 'QIM':
                # Снова кодируем 0 и 1 в тот же байт, с тем же шагом квантования
                c0 = EncodeByteQIM(c, '0', q)
                c1 = EncodeByteQIM(c, '1', q)
                # Если новое значение при кодировании 0 получилосб ближе к исходному, чем при кодировании 1,
                # значит там лежит 0, в противном слууче - 1
                c = 0 if abs(c0 - c) < abs(c1 - c) else 1
            ######################################################################

            # В младшем разряде байта c лежит интересующий нас бит сообщения
            hidden_bits += (bin(c)[-1])

        # В декодированных битах нашлась сигнатура конца сообщения
        if signbit in hidden_bits:
            # Переводим непрерывную строку из '0' и '1' (битов) в массив строк по 8 '0' и '1' (байты)
            # Учтём, что число считанных из изображения битов будет кратно 3, но не факт, что 8
            hidden_bits = [hidden_bits[i:i + 8] for i in range(0, len(hidden_bits) // 8 * 8, 8)]
            data = []  # массив с декодированными байтами сообщения
            for i in range(len(hidden_bits)):
                data.append(int(hidden_bits[i], 2))

            # Преобразуем массив байтов в строку в кодировке UTF-8, удалив из неё сигнатуру конца сообщения
            return bytes(data).decode('UTF-8')[:-len(sign)]

    return '<Скрытое сообщение не найдено>'


def Steganography():
    print('LSB - 1')
    print('PM1 - 2')
    print('QIM - 3')

    tech = ['LSB', 'PM1', 'QIM'][int(input('Метод кодирования: '))-1]
    if tech == 'QIM':
        q = int(input('Введите шаг квантования: '))
    source = input('Ведите путь до исходного изображения: ')
    message = input('Введите текст сообщения: ')
    destination = input('Введите путь для нового изображения: ')

    EncodeMessage(source, message, destination, tech, q)
    print('Сообщение:', DecodeMessage(destination, tech, q))



Steganography()
