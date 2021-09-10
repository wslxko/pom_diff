import re, os, requests, json, time, argparse


class SendDingTalk():
    def __init__(self):
        self.current_path = os.getcwd()
        self.url = "http://xxx.xxx.xxx/api/messageCenter/sendDingTalk"

    def get_git_info(self):
        with open(self.current_path + "/git_info.txt", "r", encoding="UTF-8") as f:
            git_info = ''.join(f.readlines())
            return git_info

    def get_commiter_email(self):
        string = self.get_git_info()
        re_rule = r"[\w!#$%&'*+/=?^_`{|}~-]+(?:\.[\w!#$%&'*+/=?^_`{|}~-]+)*@(?:[\w](?:[\w-]*[\w])?\.)+[\w](?:[\w-]*[\w])?"
        email_list = re.findall(re_rule, string)
        return email_list

    def get_job_url(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--url")
        args = parser.parse_args()
        url = args.url
        return url

    def send_message_dingtalk(self):
        email_list = self.get_commiter_email()
        url = self.get_job_url()
        print("本次检测到的提交人为:" + str(email_list))
        header = {"Content-Type": "application/json"}
        data = {"emailList": email_list,
                "content": "{}\n标题：检测到当前POM依赖有新版本可更新\n详情: 当前构建项目所使用POM文件依赖版本与nexus仓库中最新版本不一致，请检查\n点击查看可更新版本：{}lastSuccessfulBuild/artifact/pom_nexus_compare.txt".format(
                    time.strftime('%Y-%m-%d %H:%M:%S'), url)
                }
        data_str = json.dumps(data)
        print(data_str)
        res = requests.post(url=self.url, headers=header, data=data_str)
        res_dict = json.loads(res.text)
        print(data_str)
        if res_dict["code"] == 200:
            print("------------钉钉通知已发出------------")
        else:
            print(res.text)


if __name__ == "__main__":
    a = SendDingTalk()
    a.send_message_dingtalk()
