import hashlib
import random
import time

from lagrange.utils.crypto.tea import qqtea_encrypt
from .builder import Builder


class CommonTlvBuilder(Builder):
    @classmethod
    def _rand_u32(cls) -> int:
        return random.randint(0x0, 0xffffffff)

    @classmethod
    def t18(
            cls,
            app_id: int,
            app_client_version: int,
            uin: int,
            _ping_version: int = 0,
            _sso_version: int = 5,
            unknown: int = 0,
    ) -> bytes:
        return (
            cls()
            .write_u16(_ping_version)
            .write_u32(_sso_version)
            .write_u32(app_id)
            .write_u32(app_client_version)
            .write_u32(uin)
            .write_u16(unknown)
            .write_u16(0)
        ).pack(0x18)

    @classmethod
    def t106(
            cls,
            app_id: int,
            app_client_version: int,
            uin: int,
            salt: int,
            password_md5: bytes,
            guid: bytes,
            tgtgt_key: bytes,
            ip: bytes = bytes(4),
            save_password: bool = True,
    ) -> bytes:
        key = hashlib.md5(password_md5 + bytes(4) + cls().write_u32(salt or uin).pack()).digest()

        body = (
            cls().write_struct(
                ">HIIIIIQ",
                4,  # tgtgt version
                cls._rand_u32(),
                0,  # sso_version, depreciated
                app_id,
                app_client_version,
                uin or salt,
            )
            .write_u32(int(time.time()))
            .write_bytes(ip)
            .write_bool(save_password)
            .write_bytes(password_md5)
            .write_bytes(tgtgt_key)
            .write_u32(0)
            .write_bool(bool(guid))
            .write_u32(1)
            .write_u32(1)
            .write_string(str(uin))
        ).pack()

        return cls().write_bytes(
            qqtea_encrypt(body, key),
            with_length=True
        ).pack(0x106)

    @classmethod
    def t142(cls, apk_id: str, _version: int = 0) -> bytes:
        return (
            cls()
            .write_u16(_version)
            .write_string(apk_id[:32])
        ).pack(0x142)

    @classmethod
    def t145(cls, guid: bytes) -> bytes:
        return (
            cls()
            .write_bytes(guid)
        ).pack(0x145)

    @classmethod
    def t141(
            cls,
            sim_info: bytes,
            network_type: int = 0,
            apn: bytes = bytes(0),
            _version: int = 0
    ) -> bytes:
        return (
            cls()
            .write_u16(_version)
            .write_bytes(sim_info, with_length=True)
            .write_u16(network_type)
            .write_bytes(apn, with_length=True)
        ).pack(0x141)

    @classmethod
    def t177(cls, sdk_version: str, build_time: int = 0) -> bytes:
        return (
            cls()
            .write_struct("BI", 1, build_time)
            .write_string(sdk_version)
        ).pack(0x177)

    @classmethod
    def t191(cls, can_web_verify: int = 0) -> bytes:
        return (
            cls()
            .write_u8(can_web_verify)
        ).pack(0x191)

    @classmethod
    def t100(
            cls,
            sso_version: int,
            app_id: int,
            sub_app_id: int,
            app_client_version: int,
            sigmap: int,
            _db_buf_ver: int = 0
    ) -> bytes:
        return (
            cls()
            .write_u16(_db_buf_ver)
            .write_u32(sso_version)
            .write_u32(app_id)
            .write_u32(sub_app_id)
            .write_u32(app_client_version)
            .write_u32(sigmap)
        ).pack(0x100)

    @classmethod
    def t107(
            cls,
            pic_type: int = 1,
            cap_type: int = 0x0d,
            pic_size: int = 0,
            ret_type: int = 1,
    ) -> bytes:
        return (
            cls()
            .write_u16(pic_type)
            .write_u8(cap_type)
            .write_u16(pic_size)
            .write_u8(ret_type)
        ).pack(0x107)

    @classmethod
    def t318(cls, tgt_qr: bytes = bytes(0)) -> bytes:
        return (
            cls().write_bytes(tgt_qr)
        ).pack(0x318)

    @classmethod
    def t16a(cls, no_pic_sig: bytes) -> bytes:
        return (
            cls().write_bytes(no_pic_sig)
        ).pack(0x16a)

    @classmethod
    def t166(cls, image_type: bytes) -> bytes:
        return (
            cls().write_byte(image_type[0])
        ).pack(0x166)

    @classmethod
    def t521(cls, product_type: int = 0x13, product_desc: str = "basicim") -> bytes:
        return (
            cls()
            .write_u32(product_type)
            .write_string(product_desc)
        ).pack(0x521)