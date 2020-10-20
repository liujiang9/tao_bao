import asyncio
import time, random
from pyppeteer.launcher import launch  # 控制模拟浏览器用
from retrying import retry  # 设置重试次数用的


async def slide(page):
    slider = await page.Jeval('#nc_1_n1z', 'node => node.style')  # 是否有滑块
    if slider:
        print('当前页面出现滑块')
        # await page.screenshot({'path': './headless-login-slide.png'}) # 截图测试
        flag, page = await mouse_slide(page=page)  # js拉动滑块过去。
        if flag:
            await page.keyboard.press('Enter')  # 确保内容输入完毕，少数页面会自动完成按钮点击
            print("print enter", flag)
            # await page.evaluate('''document.getElementsByClassName("").click()''')  # 如果无法通过回车键完成点击，就调用js模拟点击登录按钮。
            await page.waitForNavigation()
    else:
        print("正常进入")
        await page.keyboard.press('Enter')
        await asyncio.sleep(2)
        # await page.evaluate('''document.getElementsByClassName("").click()''')
        await page.waitForNavigation()
        try:
            global error  # 检测是否是账号密码错误
            print("error_1:", error)
            error = await page.Jeval('.error', 'node => node.textContent')
            print("error_2:", error)
        except Exception as e:
            error = None
        finally:
            if error:
                print('确保账户安全重新入输入')
            else:
                print(page.url)
                await asyncio.sleep(10)


async def get_json(page):
    classif = ['连衣裙', '长裙', '针织衫']
    print('模拟人为操作')
    # document.querySelector("#J_SiteNavHome > div > a > span")首页
    # document.querySelector("body > div.cup.J_Cup > div > div > div.tbh-logo.J_Module.tb-pass > div > h1 > a")
    # await page.click('#J_SiteNavHome > div > a > span')
    # await page.waitForNavigation()
    # document.querySelector("#q")输入框
    for i in classif:
        await asyncio.sleep(2)
        await page.type("#q", i, {'delay': input_time_random() - 50})
        await page.keyboard.press('Enter')
        await page.waitForNavigation()
        #     document.querySelector("#J_relative > div.sort-row > div > ul > li:nth-child(2) > a")销量排行
        await page.click('#J_relative > div.sort-row > div > ul > li:nth-child(2) > a')
        await page.waitForNavigation()
        await asyncio.sleep(2)
        for a in range(0, 10):
            print('第', a, '页')
            chance_num = 0
            while chance_num < 4:
                await page.evaluate('_ => {window.scrollBy(3, window.innerHeight);}')
                chance_num += 1
                await asyncio.sleep(2)
                if chance_num == 4:
                    break
            # document.querySelector("#mainsrp-pager > div > div > div > ul > li.item.next > a > span:nth-child(1)")下一页
            await page.click('#mainsrp-pager > div > div > div > ul > li.item.next > a > span:nth-child(1)')
            await page.waitForNavigation()

        # 清空搜索框
        await page.click('#q')
        for a in range(0, 10):
            await page.keyboard.down('Backspace')
        await asyncio.sleep(2)
        print('数据采集完成')


async def get_content(username, pwd, url):
    # 以下使用await 可以针对耗时的操作进行挂起
    browser = await launch({'headless': False, })
    page = await browser.newPage()  # 启动个新的浏览器页面
    await page.setViewport({'width': 1200, 'height': 700})
    await page.setUserAgent(
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36')
    await page.goto(url)
    # 替换淘宝在检测浏览时采集的一些参数
    # 就是在浏览器运行的时候，始终让window.navigator.webdriver=false
    # navigator是windiw对象的一个属性，同时修改plugins，languages，navigator 且让
    await page.evaluate(
        '''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')  # 以下为插入中间js，将淘宝会为了检测浏览器而调用的js修改其结果。
    await page.evaluate('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
    await page.evaluate('''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
    await page.evaluate('''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')
    # 使用type选定页面元素，并修改其数值，用于输入账号密码，修改的速度仿人类操作，因为有个输入速度的检测机制
    # 因为 pyppeteer 框架需要转换为js操作，而js和python的类型定义不同，所以写法与参数要用字典，类型导入
    await page.type("#fm-login-id", username, {'delay': input_time_random() - 50})
    await page.type("#fm-login-password", pwd, {'delay': input_time_random()})
    # await page.screenshot({'path': './headless-test-result.png'})    # 截图测试
    await asyncio.sleep(2)
    # 检测页面是否有滑块。原理是检测页面元素。
    await slide(page)
    # await asyncio.sleep(20)
    await get_json(page)
    await page.close()


def retry_if_result_none(result):
    return result is None


@retry(retry_on_result=retry_if_result_none, )
async def mouse_slide(page=None):
    await asyncio.sleep(2)
    try:
        # 鼠标移动到滑块，按下，滑动到头（然后延时处理），松开按键
        await page.hover('#nc_1_n1z')  # 不同场景的验证码模块能名字不同。
        await page.mouse.down()
        await page.mouse.move(2000, 0, {'delay': random.randint(1000, 2000)})
        await page.mouse.up()
    except Exception as e:
        print(e, ':验证失败')
        return None, page
    else:
        await asyncio.sleep(2)
        # 判断是否通过
        slider_again = await page.Jeval('.nc-lang-cnt', 'node => node.textContent')
        if slider_again != '验证通过':
            return None, page
        else:
            # await page.screenshot({'path': './headless-slide-result.png'}) # 截图测试
            print('验证通过')
            return 1, page


def input_time_random():
    return random.randint(100, 151)


if __name__ == '__main__':
    username = '账户'  # 淘宝用户名
    pwd = '密码'  # 密码
    # 淘宝的迷你登录界面
    url = 'https://login.taobao.com/'
    loop = asyncio.get_event_loop()  # 协程，开启个无限循环的程序流程，把一些函数注册到事件循环上。当满足事件发生的时候，调用相应的协程函数。
    loop.run_until_complete(get_content(username, pwd, url))  # 将协程注册到事件循环，并启动事件循环
