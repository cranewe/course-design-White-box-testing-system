class Rule:
    def __init__(self, conditions, conclusion, name):
        self.conditions = set(conditions)
        self.conclusion = conclusion
        self.name = name

class ExpertSystem:
    def __init__(self, rules, facts):
        self.rules = rules
        self.facts = set(facts)
        self.fired_rules = []

    def match_and_fire(self):
        applied = True
        while applied:
            applied = False
            for rule in self.rules:
                if rule.conditions.issubset(self.facts) and rule.conclusion not in self.facts:
                    print(f"【应用规则】{rule.name}: IF {' AND '.join(rule.conditions)} THEN {rule.conclusion}")
                    self.facts.add(rule.conclusion)
                    self.fired_rules.append(rule.name)
                    applied = True

    def get_results(self):
        return self.facts, self.fired_rules

if __name__ == "__main__":
    # 定义规则
    rules = [
        Rule(["树叶变黄", "有虫孔"], "可能患有天牛病", "R1"),
        Rule(["树干开裂", "有流胶现象"], "可能患有树干腐烂病", "R2"),
        Rule(["树叶发黑", "有霉斑"], "可能患有煤污病", "R3"),
        Rule(["可能患有天牛病"], "建议使用天牛专用杀虫剂处理", "R4"),
        Rule(["可能患有树干腐烂病"], "建议切除病变部位并消毒", "R5"),
        Rule(["可能患有煤污病"], "建议清除表面霉菌并喷药", "R6"),
        Rule(["树叶变黄"], "土壤可能缺氮", "R7"),
        Rule(["土壤可能缺氮"], "建议施加氮肥", "R8"),
        Rule(["叶片枯萎", "树干无弹性"], "可能枯死", "R9"),
        Rule(["可能枯死"], "建议砍除重栽", "R10"),
    ]

    # 输入初始事实（可修改）
    initial_facts = input("请输入初始事实（用逗号分隔）：\n").split("，")
    initial_facts = [fact.strip() for fact in initial_facts]

    # 创建专家系统并运行推理
    system = ExpertSystem(rules, initial_facts)
    system.match_and_fire()

    # 输出结果
    final_facts, fired_rules = system.get_results()
    print("\n【推理结束】最终事实如下：")
    for fact in final_facts:
        print(" -", fact)

    print("\n【使用的规则】")
    for rule in fired_rules:
        print(" -", rule)
