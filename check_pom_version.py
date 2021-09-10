import os, requests, re, copy


class CheckPomVersion():
    def __init__(self):
        self.current_path = os.getcwd()
        self.diff_pom_path = self.current_path.replace("/jenkins/workspace", "/pom_diff")
        self.diff_pom_file = self.diff_pom_path + '/' + 'pom_new.txt'
        self.bash_url = "http://xxx.xxx.xxx/service/rest/repository/browse"
        self.url_list = []
        self.url_version = []
        self.re_group_version_list = []
        self.url_version_dict = {}
        self.env_dict = {"dev": "/xxx-dev-public", "qa": "/xxx-qa-public", "release": "/xxx-pre-public",
                         "master": "/xxx-prd-public"}

    def get_url_list(self, env):
        self.bash_url = self.bash_url + self.env_dict.get(env)
        with open(self.diff_pom_file) as pom:
            pom_lines = pom.readlines()
            for pom_line in pom_lines:
                jar_url = self.bash_url + pom_line.replace(".repository", "")
                pattern = re.compile('[0-9]+')
                match = pattern.findall(jar_url)
                # if "SNAPSHOT" in jar_url:
                if match:
                    jar_url_spilt = jar_url.split('/')
                    other_jar_url_spilt = copy.deepcopy(jar_url_spilt)
                    del other_jar_url_spilt[-1]
                    del other_jar_url_spilt[-1]
                    new_jar_url = '/'.join(other_jar_url_spilt)
                    self.url_list.append(new_jar_url)
                    self.url_version.append(jar_url_spilt[-2])
                    self.url_version_dict[new_jar_url] = jar_url_spilt[-2]

    def get_max_version(self, env):
        if os.path.exists(self.current_path + "/pom_nexus_compare_result.txt"):
            os.remove(self.current_path + "/pom_nexus_compare_result.txt")
        self.get_url_list(env)
        for url in self.url_list:
            self.re_group_version(url)
            self.re_group_version_list.sort(reverse=True)
            current_url_version = self.url_version_dict.get(url)
            if current_url_version in self.re_group_version_list:
                if current_url_version != self.re_group_version_list[0]:
                    self.write_txt("nexus依赖地址：" + url + "\n" + "当前依赖最大版本为: " + str(
                        self.re_group_version_list[0]) + "\n" + "当前依赖所使用版本为: " + self.url_version_dict.get(
                        url) + "\n" + "注意：当前依赖所使用的的版本不为最大版本" + "\n\n")
            else:
                if len(self.re_group_version_list) != 0:
                    self.write_txt("nexus依赖地址：" + url + "\n" + "当前依赖最大版本为: " + str(
                        self.re_group_version_list[0]) + "\n" + "当前依赖所使用版本为: " + self.url_version_dict.get(
                        url) + "\n" + "当前依赖版本不存在" + "\n\n")
                else:
                    self.write_txt("nexus依赖地址：" + url + "\n" + "当前依赖最大版本为: 当前nexus依赖地址不存在"+ "\n" + "当前依赖所使用版本为: " + self.url_version_dict.get(
                        url) + "\n" + "当前依赖版本不存在" + "\n\n")

            self.re_group_version_list = []

    def re_group_version(self, url):
        res = requests.get(url)
        re_rule = r'(?<=<a).*?(?=/a>)'
        re_rule1 = r'(?<==").*?(?=">)'
        li = re.findall(re_rule, res.text)
        for i in li:
            version = re.findall(re_rule1, i)
            version_str = "".join(version)
            if "xml" not in version_str and version_str != "../":
                self.re_group_version_list.append(version_str[:-1])

    def write_txt(self, content):
        with open(self.current_path + "/pom_nexus_compare_result.txt", "a") as f:
            f.write(content)


if __name__ == "__main__":
    a = CheckPomVersion()
    a.get_max_version("qa")
