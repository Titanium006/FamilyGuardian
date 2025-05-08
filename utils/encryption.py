# 文件加解密
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


# 加密方法
def func_encrypt_config(_key, plain_text):
    """
    使用AES加密给定的明文
    :param _key:加密密钥
    :param plain_text:需要加密的明文
    :return:加密后的文本, 包含初始化向量和密文
    """
    # 创建AES加密器, 使用CBC模式
    cipher = AES.new(_key, AES.MODE_CBC)

    # 对明文进行填充并加密
    ciphertext = cipher.encrypt(pad(plain_text.encode(), AES.block_size))

    # 获取初始化向量, 并将其与密文一起进行Base64编码
    iv = base64.b64encode(cipher.iv).decode()
    encrypted_text = base64.b64encode(ciphertext).decode()

    # 返回拼接后的初始化向量和密文
    return iv + encrypted_text


# 解密方法
def func_decrypt_config(_key, encrypted_text):
    """
    使用AES解密给定的密文
    :param _key:解密密钥
    :param encrypted_text:加密后的文本, 包含初始化向量和密文
    :return:解密后的明文
    """
    # 提取并解码Base64编码的初始化向量和密文
    iv = base64.b64decode(encrypted_text[:24])
    ciphertext = base64.b64decode(encrypted_text[24:])

    # 创建AES解密器, 使用CBC模式和提取的初始化向量
    cipher = AES.new(_key, AES.MODE_CBC, iv)

    # 解密密文并去除填充, 返回明文
    decrypted_text = unpad(cipher.decrypt(ciphertext), AES.block_size).decode()
    return decrypted_text
