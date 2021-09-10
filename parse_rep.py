import os, difflib, shutil


class Parse_rep():
    def diff_rep(self):
        current_path = os.getcwd()
        diff_rep_path = current_path.replace("/jenkins/workspace", "/rep_diff")
        # diff_rep_path = current_path.replace("parse-nexus-pom", "rep_diff")
        diff_rep_file = diff_rep_path + '/' + 'rep_new.txt'

        if os.path.exists(diff_rep_path):
            pass
        else:
            os.makedirs(diff_rep_path)
        for root, dirs, files in os.walk("./.repository"):
            for file in files:
                with open(diff_rep_file, "w") as a:
                    a.write(os.path.join(root, file) + '\n')

        if os.path.exists(diff_rep_path + "/" + "rep_old.txt"):
            with open(diff_rep_path + "/" + "rep_old.txt") as rep_old:
                rep_old_lines = rep_old.readlines()
            with open(diff_rep_path + "/" + "rep_new.txt") as rep_new:
                rep_new_lines = rep_new.readlines()
            print("--------------当前repository与上一次对比结果--------------")
            if rep_old_lines == rep_new_lines:
                print("\033[1:34m--------------本次repository文件与上一次repository文件一致--------------\033[0m")
            else:
                print("\033[1:34m--------------本次repository文件对比不一致，详情查看归档html文件--------------\033[0m")
                d = difflib.HtmlDiff()
                htmlContent = d.make_file(rep_old_lines, rep_new_lines)
                with open(diff_rep_path + "/" + "rep_diff.html", "w") as diffhtml:
                    diffhtml.write(htmlContent)
                shutil.copy(diff_rep_path + "/" + "rep_diff.html", current_path)
            rep_old.close()
            rep_new.close()
            if os.path.exists(diff_rep_path + "/" + "rep_old.txt"):
                os.remove(diff_rep_path + "/" + "rep_old.txt")
                os.rename(diff_rep_path + "/" + "rep_new.txt", diff_rep_path + "/" + "rep_old.txt")
        else:
            print("首次执行，无法对比repository文件差异")
            os.rename(diff_rep_path + "/" + "rep_new.txt", diff_rep_path + "/" + "rep_old.txt")


if __name__ == "__main__":
    a = Parse_rep()
    a.diff_rep()
