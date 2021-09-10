from xml.dom.minidom import parse
import xml.dom.minidom
import os, difflib, shutil
from check_pom_version import CheckPomVersion
import argparse


class Parse_pom():
    def __init__(self):
        DOMTree = xml.dom.minidom.parse("pom.xml")
        self.collection = DOMTree.documentElement
        self.dependencys = self.collection.getElementsByTagName("dependency")
        self.model_version = self.collection.getElementsByTagName("modelVersion")[0].childNodes[0].data
        self.catalogue_list = []
        self.current_path = os.getcwd()
        self.check_pom_version = CheckPomVersion()

    def begin_parse(self):
        print("------------开始解析pom文件------------")
        for dependency in self.dependencys:
            self.groupId = dependency.getElementsByTagName("groupId")[0].childNodes[0].data
            self.artifactId = dependency.getElementsByTagName("artifactId")[0].childNodes[0].data
            if dependency.getElementsByTagName("version"):
                self.version = dependency.getElementsByTagName("version")[0].childNodes[0].data
                if "$" in self.version:
                    if self.collection.getElementsByTagName("properties"):
                        properties = self.collection.getElementsByTagName("properties")[0]
                        if properties.getElementsByTagName(self.version[2:-1]):
                            self.version = properties.getElementsByTagName(self.version[2:-1])[0].childNodes[0].data
                catalogue = ".repository/" + self.groupId.replace(".",
                                                                  "/") + "/" + self.artifactId + "/" + self.version + "/"
                self.catalogue_list.append(catalogue)
            else:
                catalogue = ".repository/" + self.groupId.replace(".", "/") + "/" + self.artifactId + "/"
                self.catalogue_list.append(catalogue)
        return self.catalogue_list

    def path_exist(self):
        catalogue_list = self.begin_parse()
        for catalogue in catalogue_list:
            if os.path.isdir(catalogue):
                print(catalogue + "***依赖存在")
            else:
                print(catalogue + "***依赖有更改或不存在，请检查")

    def diff_file(self):

        current_path = os.getcwd()
        # diff_pom_path = current_path.replace("/jenkins/workspace", "/pom_diff")
        diff_pom_path = self.current_path.replace("parse-nexus-pom", "pom_diff")
        diff_pom_file = diff_pom_path + '/' + 'pom_new.txt'
        if os.path.exists(diff_pom_path):
            pass
        else:
            os.makedirs(diff_pom_path)
        with open(diff_pom_file, "w") as a:
            for diff in self.catalogue_list:
                if diff != "[" or "]":
                    a.write(diff + "\n")

        if os.path.exists(diff_pom_path + "/" + "pom_old.txt"):
            with open(diff_pom_path + "/" + "pom_old.txt") as pom_old:
                pom_old_lines = pom_old.readlines()
            with open(diff_pom_path + "/" + "pom_new.txt") as pom_new:
                pom_new_lines = pom_new.readlines()

            parser = argparse.ArgumentParser()
            parser.add_argument("--env", default="qa")
            args = parser.parse_args()
            e = args.env
            self.check_pom_version.get_max_version(e)

            d = difflib.Differ()
            diff = d.compare(pom_old_lines, pom_new_lines)
            print("\033[1:34m--------------当前pom与上一次对比结果--------------\033[0m")
            if pom_old_lines == pom_new_lines:
                print("\033[1:34m--------------本次pom文件与上一次pom文件一致--------------\033[0m")
            else:
                print("\033[1:34m--------------本次pom文件对比不一致，详情查看归档html文件--------------\033[0m")
                print('\n'.join(diff))
                htmldiff = difflib.HtmlDiff()
                htmlContent = htmldiff.make_file(pom_old_lines, pom_new_lines)
                with open(diff_pom_path + "/" + "pom_diff.html", "w") as diffhtml:
                    diffhtml.write(htmlContent)
                shutil.copy(diff_pom_path + "/" + "pom_diff.html", self.current_path)
            pom_old.close()
            pom_new.close()
            if os.path.exists(diff_pom_path + "/" + "pom_old.txt"):
                os.remove(diff_pom_path + "/" + "pom_old.txt")
                os.rename(diff_pom_path + "/" + "pom_new.txt", diff_pom_path + "/" + "pom_old.txt")
        else:
            print("\033[1:34m--------------首次执行，无法对比pom文件差异--------------\033[0m")
            os.rename(diff_pom_path + "/" + "pom_new.txt", diff_pom_path + "/" + "pom_old.txt")


if __name__ == "__main__":
    a = Parse_pom()
    a.path_exist()
    a.diff_file()
