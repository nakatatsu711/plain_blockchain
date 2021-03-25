import hashlib
import datetime
import time
import json


# 難易度
INITIAL_BITS = 0x1e777777
# 最大値
MAX_32BIT = 0xffffffff


class Block():
    '''
    個々のブロックを定義
    '''

    def __init__(self, index, prev_hash, data, timestamp, bits):
        '''
        初期化
        '''

        self.index = index
        self.prev_hash = prev_hash
        self.data = data
        self.timestamp = timestamp
        self.bits = bits
        self.nonce = 0
        self.elapsed_time = ''
        self.block_hash = ''

    def __setitem__(self, key, value):
        '''
        オブジェクトを辞書型で扱う（特殊メソッド）
        '''

        # 属性を追加（第1引数：オブジェクト、第2引数：属性名、第3引数：属性値）
        setattr(self, key, value)

    def to_json(self):
        '''
        1つのブロックにまとめる
        '''

        # rjust：全部で8文字になるように右寄せ
        return {
            'index': self.index,
            'prev_hash': self.prev_hash,
            'stored_data': self.data,
            'timestamp': self.timestamp.strftime('%Y/%m/%d %H:%M:%S'),
            'bits': hex(self.bits)[2:].rjust(8, '0'),
            'nonce': hex(self.nonce)[2:].rjust(8, '0'),
            'elapsed_time': self.elapsed_time,
            'block_hash': self.block_hash
        }

    def calc_blockhash(self):
        '''
        ブロックヘッダを構築し、ハッシュ化
        '''

        blockheader = str(self.index) + str(self.prev_hash) + str(self.data) + \
            str(self.timestamp) + hex(self.bits)[2:] + str(self.nonce)
        h = hashlib.sha256(blockheader.encode()).hexdigest()
        self.block_hash = h
        return h

    def calc_target(self):
        '''
        ターゲットを算出
        '''

        # exponentを算出（24ビット右シフトし、3を引く）
        exponent_bytes = (self.bits >> 24) - 3
        # バイトをビットに変換
        exponent_bits = exponent_bytes * 8
        # coefficientを算出（論理積を取り、先頭2桁を排除）
        coefficient = self.bits & 0xffffff
        # exponent_bits分、左シフト
        return coefficient << exponent_bits

    def check_valid_hash(self):
        '''
        ハッシュ値がターゲットより小さいかどうか判定
        '''

        return int(self.calc_blockhash(), 16) <= self.calc_target()


class Blockchain():
    '''
    ブロックの関係性を定義
    '''

    def __init__(self, initial_bits):
        '''
        初期化
        '''

        self.chain = []
        self.initial_bits = initial_bits

    def add_block(self, block):
        '''
        ブロックにデータを追加
        '''

        self.chain.append(block)

    def getblockinfo(self, index=-1):
        '''
        chain配列の最後の要素を取り出し、JSON形式で出力
        '''

        # indent：インデントの大きさ、sort_keys：キーでソートを可能にする、ensure_ascii：日本語表記を可能にする
        return print(json.dumps(self.chain[index].to_json(), indent=2, sort_keys=True, ensure_ascii=False))

    def mining(self, block):
        '''
        ブロックをつなげる
        '''

        start_time = int(time.time() * 1000)
        while True:
            for n in range(MAX_32BIT + 1):
                block.nonce = n
                if block.check_valid_hash():
                    end_time = int(time.time() * 1000)
                    block.elapsed_time = str((end_time - start_time) / 1000.0) + '秒'
                    self.add_block(block)
                    self.getblockinfo()
                    return
            # タイムスタンプを調整
            new_time = datetime.datetime.now()
            if new_time == block.timestamp:
                block.timestamp += datetime.timedelta(seconds=1)
            else:
                block.timestamp = new_time

    def create_genesis(self):
        '''
        ジェネシスブロックを生成
        '''

        genesis_block = Block(0,
            '0000000000000000000000000000000000000000000000000000000000000000',
            'ジェネシスブロック', datetime.datetime.now(), self.initial_bits)
        self.mining(genesis_block)

    def add_newblock(self, i):
        '''
        Blockクラスをインスタンス化
        '''

        last_block = self.chain[-1]
        block = Block(i + 1, last_block.block_hash, 'ブロック ' + str(i + 1),
            datetime.datetime.now(), last_block.bits)
        self.mining(block)


if __name__ == '__main__':
    # Blockchainクラスをインスタンス化
    bc = Blockchain(INITIAL_BITS)
    # ジェネシスブロックを生成
    print('ジェネシスブロックを作成中・・・')
    bc.create_genesis()
    # 新規ブロックを生成
    for i in range(30):
        print(str(i + 2) + '番目のブロックを作成中・・・')
        bc.add_newblock(i)
