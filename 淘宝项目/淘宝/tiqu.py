import json
import os
import re
import time
from xlsxwriter import Workbook


def json_alter():
    """
    修改文件格式
    :return:
    """
    json_list = r'./json/'
    filenames = os.listdir(json_list)
    print('filenames', filenames)
    for filename in filenames:
        with open((os.path.join(json_list + filename)), 'r', encoding='utf-8') as f:
            f2 = f.read()
            if f2:
                pass
            else:
                os.remove(json_list + filename)
        with open((os.path.join(json_list + filename)), 'r', encoding='utf-8') as f1:
            fp = f1.read()
            print(fp)
            aa1 = re.findall(r'\((.*?)\}\);', fp)
            if aa1:
                print(aa1)
                with open(json_list + filename, "w", encoding="utf-8") as f1:
                    f1.write(aa1[0] + '}')


def main():
    """
    获取json内数据
    :return:
    """
    # json_alter()  # 删除空文件夹以及修改为json格式,只运行一次
    list = []
    json_list = r'./json/'
    filenames = os.listdir(json_list)
    # print('filenames1', filenames)
    for filename in filenames:
        fp = open(json_list + filename, 'r', encoding='utf-8')
        print(fp)
        json_data = json.load(fp)
        # print(json_data)
        """
            "title": "茶歇设计感法式小众显高收腰显瘦2020年新款夏气质\u003cspan class\u003dH\u003e连衣裙\u003c/span\u003e子秋长裙",
            "raw_title": "茶歇设计感法式小众显高收腰显瘦2020年新款夏气质连衣裙子秋长裙",
            "pic_url": "//g-search2.alicdn.com/img/bao/uploaded/i4/i2/2455352241/O1CN017OZFui1SQQC5f9uTk_!!0-item_pic.jpg",
            "detail_url": "//detail.tmall.com/item.htm?id\u003d622042494496\u0026ns\u003d1\u0026abbucket\u003d15",
            "view_price": "49.90",
            "view_fee": "0.00",
            "item_loc": "广东 广州",
            "view_sales": "2523人收货",
            "comment_count": "2138",
            "user_id": "2455352241",
            "nick": "y6y旗舰店",
        """
        for data in json_data['mods']['itemlist']['data']['auctions']:
            print('第一页')
            raw_title = data['raw_title']
            detail_url = data['detail_url']
            view_price = data['view_price']
            view_fee = data['view_fee']
            item_loc = data['item_loc']
            comment_count = data['comment_count']
            nick = data['nick']
            try:
                view_sales = data['view_sales']
            except:
                print('缺失：', nick)
            item = {}
            item['raw_title'] = raw_title
            item['detail_url'] = 'https:' + detail_url
            item['view_price'] = view_price
            item['view_fee'] = view_fee
            item['item_loc'] = item_loc
            item['view_sales'] = view_sales
            item['comment_count'] = comment_count
            item['nick'] = nick
            list.append(item)
    time.sleep(10)
    ordered_list = ['raw_title', 'detail_url', 'view_price', 'view_fee', 'item_loc', 'view_sales', 'comment_count',
                    'nick', ]  # 按索引列出对象调用，但dict对象随机调用项
    wb = Workbook("../提取/女装销售情况.xlsx")
    ws = wb.add_worksheet("")  # 或者留空，默认名称为“Sheet 1”
    first_row = 0
    for header in ordered_list:
        col = ordered_list.index(header)  # 维持顺序。
        ws.write(first_row, col, header)  # 我们已经写了第一行，这也是工作表的标题。
    row = 1
    for player in list:
        for _key, _value in player.items():
            col = ordered_list.index(_key)
            ws.write(row, col, _value)
        row += 1  # 进入下一行
    wb.close()


if __name__ == '__main__':
    # mobile = Method.createPhone()
    main()
