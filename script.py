#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComfyUI 图片生成脚本
用法: python script.py [prompt]
如果不提供 prompt,使用随机生成的提示词
"""

import sys
import os
import json
import random
import time
import urllib.request
import urllib.parse

# 配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")

# 加载配置
def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def pick_element(lst, index):
    """根据索引值从列表中选取元素
    - index >= 0 且 index < len(lst): 按索引取值
    - index == -1 或 index >= len(lst): 随机取值
    """
    if index == -1 or index >= len(lst):
        return random.choice(lst)
    else:
        return lst[index]

# 随机 prompt 生成器
def generate_random_prompt(config):
    """根据配置生成女孩 prompt"""
    base_prompt = "年轻女孩半身写真,头顶留空白,不要占满画面。人物处于画面右边三分之一处。五官精致立体,白皙冷白皮,水润粉红唇,皮肤细腻通透,温柔慵懒神态。"
    haircolors = ["","黑色", "深棕色", "酒红色", "浅棕色"] 
    hairstyles = [
        "齐耳短发","微卷中分长发","中长发","长发","长直发", "长卷发","低马尾","高马尾"
    ]
    eyes = ["","面朝镜头,直视镜头","侧对镜头看向远方","镜头俯拍,抬头看向镜头","镜头仰拍,低头看向镜头"] 
    glass = ["","无框眼镜","金丝细框小圆框眼镜","细框黑框眼镜"] # "细框黑框眼镜",
    bodies = [
        "small_breasts,微乳,平胸", "huge_breasts,巨乳"
    ]
    poses = ["一手整理头发","一手扶额头", "一手撑下巴","一手托胸部","一手托着乳房下沿"] #,"一手握拳放在胸口","挥手", "OK手势","V手势","嘘手势","点赞手势","双手交叉","摊手","双手伸展,掌心朝前做拥抱动作"]
    expressions = ["","露齿妩媚地笑", "微笑", "浅笑", "妩媚地笑","张口大笑"]

    color = [
        "","半透明", 
        "白色", "黑色", "金色", "银色",
        "白色暗纹", "乳白色暗纹", "米白色暗纹", "浅土黄色暗纹","橙色暗纹",
        "黑色暗纹", "浅灰色暗纹", "深灰色暗纹", "藏青色暗纹",
        "粉蓝色","粉绿色", "粉红色","枣红色", "藕青色", "深紫色",
        #"云纹","钻石菱形纹","龙纹", "凤纹", "黑色水墨植物印花" ,
        #"鱼骨纹","扎染纹","卷草纹","联珠纹","灯芯绒","佩斯利纹","华夫格纹"
    ]
    clothes = [
        "全身赤裸,completed_nude,small_nipples",
        "棉质紧身裹臀三角裤,上身赤裸,topless,small_nipples",
        #"绕颈围裙,围裙内真空,completed_nude,big_ass,LV镶钻耳钉",
        "白色浴巾",
        "紧身小背心", 
        #"无肩带运动内衣",
        #"紧身运动内衣",
        #"紧身瑜伽服",
        #"紧身连体蕾丝裤袜"
        #"单斜切肩袖无肩带连体紧身泳衣",
        
        #"珍珠耳钉,蕾丝女仆服装",
        #"钻石耳钉,身穿白雪公主服饰",
        #"珍珠耳钉,身穿月白薄纱广袖长袍,内衬正红修身连衣裙,高收腰",
        #"珍珠耳钉,身穿嫦娥服饰,内层素白月光缎高腰齐胸襦裙,中层淡蓝薄纱广袖上衣,外层超长雾白透纱披帛,裙身暗绣桂树流云满月浅纹",
        #"珍珠耳钉,身穿南航空姐制服,酒红色无袖马甲,表面有细腻的纹理感,内搭白色翻领长袖衬衫,领口露出蓝粉相间的丝巾,头戴酒红色空姐帽,胸前铭牌写着字母Q",
        #"黄金耳钉,身穿鎏金带翅膀的黄金圣衣,立体雕花肩甲,浮雕胸甲,金属铠甲,古希腊圣战士造型,神圣华丽,光影金属质感,史诗感",
        
        #"秦代汉服", "汉朝风格汉服", "唐代汉服","宋代汉服", "明代汉服",  
        #"和服","日式低领短袖浴衣","修士袍","道士长袍",
        #"珍珠耳钉,身穿敦煌飞天服饰", 
        #"珍珠耳钉,紧身短袖有领校服,白身宝蓝袖",
        #"古希腊风格衣服,LV镶钻耳钉",
        #"古罗马风格布衣,LV镶钻耳钉",
        #"绕颈肩带无袖旗袍,单粒珍珠耳钉","高领无袖旗袍,单粒珍珠耳钉","无领短袖旗袍,单粒珍珠耳钉",
        #"珍珠耳钉,白色无肩带短袖婚纱,白色蕾丝手套,钻石发冠,珍珠项链,手捧玫瑰花束",  

        #"紧身薄款毛衣裙,LV镶钻耳钉",
        #"露脐小西装,包臀短裙,LV镶钻耳钉",
        #"宽松简约V领长袖缎面衬衫,LV镶钻耳钉",
        #"无肩带裹胸,LV镶钻耳钉", 
        #"短袖丝绸衬衫,LV镶钻耳钉", 
        #"宽松吊带超短裙,LV镶钻耳钉","紧身吊带超短裙,LV镶钻耳钉",
        #"丝绸露肩罩衫,无肩带,LV镶钻耳钉", 
        #"短款薄款露脐衬衫,前襟打结包裹胸部,LV镶钻耳钉",
        #"紧身短袖露肩毛衣,无肩带,LV镶钻耳钉","紧身短袖立领毛衣,LV镶钻耳钉",
        #"低领丝绸睡裙",
    ]
    scenes = [
        "青色墙壁,无家具无其他装饰", 

        "坐在半人高的木质大浴桶里,浴桶水面铺满玫瑰花瓣,女孩上半身伸出水面,水珠在乳房流淌,一手扶着桶沿",
        "站在浴室淋浴,花洒喷水到肩膀,水珠布满身体,水流从胸部缓缓流下",
        "坐在打开的马桶上,内裤褪到膝盖",
        "酒店浴室,背景是浴室墙壁", 
        "坐在酒店大浴缸里",
        "坐在户外温泉池里",

        "沿海盘山公路,路边浅蓝色公路护栏,护栏旁长满茂密翠绿灌木与白色小花,远处背景是滨海小镇建筑群,红色尖顶欧式小屋,大片海面,朦胧远山与风力发电机,万里无云的浅蓝色天空",
        "茶室内,坐在红木茶台边的黑色办公椅上泡茶喝茶,茶台桌面放着一个长方形黑色石头茶盘,茶盘上放着两只白色陶瓷功夫茶杯", 
        "欧式老建筑拱形长廊阳台,站在米白色落地拱形窗边,白色百叶窗向外敞开,窗框有磨损",
        "站在海边悬崖礁石岸边,远处开阔深蓝色海面,海面竖立着一排白色海上风力发电机",

        "坐在黑色皮质单人沙发上,一手搭在沙发扶手",
        "坐在酒店床上,背景是白色床单,无其他装饰",
        "挺直身体坐在汽车副驾,身体前倾",
        "盘腿坐在黑色皮质长沙发上",
        "坐在阶梯台阶上,镜头仰拍",
        "坐在秋千架上,手扶着绳索",
        "坐在摩托车上,身子前倾",
        "坐在地铁车厢玩手机", 
        "坐在学校书桌旁看书",
        "坐在酒店贵妃椅",
        "坐滑梯向下滑",
        "坐在办公椅上",
        "坐在钢琴前",


        "侧躺在沙发上,面向镜头", 
        "侧躺在酒店床上,看向镜头,背景是白色床单,无其他装饰",
       
        "趴伏在酒店床上,抬头看镜头,背景是白色床单,无其他装饰",
        "跪在酒店床上,背景是白色床单,无其他装饰",
        "上半身趴在办公桌上,胸部搁在桌面", 
        "在瑜伽垫上做平板支撑,双肘撑地",
        "跪在寺庙蒲团上,双手合十祈祷",
        "躺在酒店贵妃椅上",
        "跪坐在瑜伽垫上", 


        "站在花树下赏花,背景是满树的樱花", 
        "站在校道上,两旁是树",
        "站在舞台,手拿话筒",

        "羽毛球场上挥羽毛球拍",
        "乒乓球台前打乒乓球",
        "网球场上挥网球拍",
        "篮球场上投篮",

        "古典园林赏花,背景是盛开的牡丹",
        "教室里,背景是落地黑板",
        "在操场单杠做引体向上",
        "中式园林里的小轩窗",
        "深夜河堤路灯下",
        "黄昏的海边沙滩", 
        "日式公共澡堂",
        "室内灯光泳池", 
        "游泳池内仰泳",
        "坐在黄包车上",
        "山顶天池边",
        "中式庭院",
        "古城墙上",
        "古典屏风",
        "台球桌边", 
        "图书堆中",
        "飞机舱内", 
        "教堂里", 
        "咖啡店", 
        "酒柜边", 
        "灶台旁", 
        "草地上", 
        "稻田里", 
        "大街上",
        "雪地里"

    ]
    prompt_cfg = config.get("prompt_config", {})
    haircolor = pick_element(haircolors, prompt_cfg.get("haircolor", -1))
    hairstyle = pick_element(hairstyles, prompt_cfg.get("hairstyle", -1))
    eye = pick_element(eyes, prompt_cfg.get("eye", -1))
    glasses = pick_element(glass, prompt_cfg.get("glasses", -1))
    color_choice = pick_element(color, prompt_cfg.get("color", -1))
    clothing = pick_element(clothes, prompt_cfg.get("clothing", -1))
    body = pick_element(bodies, prompt_cfg.get("body", -1))
    scene = pick_element(scenes, prompt_cfg.get("scene", -1))
    pose = pick_element(poses, prompt_cfg.get("pose", -1))
    expression = pick_element(expressions, prompt_cfg.get("expression", -1))
    suffix = ",8K超清,高质量,细节丰富,背景虚化,浅景深,电影感光影,艺术照风格"

    prompt = (
        base_prompt + haircolor + hairstyle + "," + glasses + "," + eye + "," +
        color_choice + clothing + "," + body + "," + scene + "," +
        pose + "," + expression + suffix
    )
    return prompt

# 检查服务可用性
def check_service(host):
    try:
        req = urllib.request.Request(
            "http://" + host + "/system_stats",
            headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception as e:
        print("ComfyUI 服务不可用: " + str(e))
        return False

# 构建工作流
def build_prompt(user_prompt, config):
    seed = random.randint(1, 1000000000) if config.get("seed", 0) == 0 else config["seed"]

    return {
        "prompt": {
            "16": {
                "class_type": "UNETLoader",
                "inputs": {
                    "unet_name": config["unet_name"],
                    "weight_dtype": config["unet_dtype"]
                }
            },
            "17": {
                "class_type": "VAELoader",
                "inputs": {
                    "vae_name": config["vae_name"]
                }
            },
            "28": {
                "class_type": "CLIPLoaderGGUF",
                "inputs": {
                    "clip_name": config["clip_name"],
                    "type": config["clip_type"]
                }
            },
            "45": {
                "class_type": "EmptyLatentImage",
                "inputs": {
                    "width": config["width"],
                    "height": config["height"],
                    "batch_size": 1
                }
            },
            "6": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": user_prompt,
                    "clip": ["28", 0]
                }
            },
            "62": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": "blurry,ugly,bad,bra",
                    "clip": ["28", 0]
                }
            },
            "52": {
                "class_type": "LoraLoaderModelOnly",
                "inputs": {
                    "model": ["16", 0],
                    "lora_name": config["lora1_name"],
                    "strength_model": config["lora1_strength"]
                }
            },
            "53": {
                "class_type": "LoraLoaderModelOnly",
                "inputs": {
                    "model": ["52", 0],
                    "lora_name": config["lora2_name"],
                    "strength_model": config["lora2_strength"]
                }
            },
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": seed,
                    "steps": config["steps"],
                    "cfg": config["cfg"],
                    "sampler_name": "er_sde",
                    "scheduler": "sgm_uniform",
                    "denoise": 1.0,
                    "model": ["53", 0],
                    "positive": ["6", 0],
                    "negative": ["62", 0],
                    "latent_image": ["45", 0]
                }
            },
            "8": {
                "class_type": "VAEDecode",
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["17", 0]
                }
            },
            "9": {
                "class_type": "SaveImage",
                "inputs": {
                    "filename_prefix": "openclaw",
                    "images": ["8", 0]
                }
            }
        }
    }

# 发送请求
def submit_prompt(host, prompt_data, timeout):
    data = json.dumps(prompt_data).encode("utf-8")
    req = urllib.request.Request(
        "http://" + host + "/prompt",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    response = urllib.request.urlopen(req, timeout=timeout)
    result = json.loads(response.read().decode())
    return result.get("prompt_id")

# 轮询等待完成
def wait_for_completion(host, prompt_id, timeout, poll_interval):
    max_attempts = timeout // poll_interval

    for i in range(max_attempts):
        time.sleep(poll_interval)
        req = urllib.request.Request(
            "http://" + host + "/history/" + str(prompt_id),
            headers={"Content-Type": "application/json"}
        )
        resp = json.loads(urllib.request.urlopen(req).read().decode())
        status = resp.get(prompt_id, {}).get("status", {})

        if status.get("completed"):
            return resp.get(prompt_id, {}).get("outputs", {}), None
        elif status.get("err_msg"):
            return None, status.get("err_msg")



    return None, "超时"

# 下载图片
def download_images(host, outputs, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    saved_paths = []

    for node_id, node_output in outputs.items():
        if "images" in node_output:
            for img in node_output["images"]:
                filename = img["filename"]
                subfolder = img.get("subfolder", "")
                img_url = "http://" + host + "/view?filename=" + filename
                if subfolder:
                    img_url += "&subfolder=" + subfolder

                local_path = os.path.join(output_dir, filename)
                # 防止文件名冲突：已存在则自动加序号
                if os.path.exists(local_path):
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(os.path.join(output_dir, f"{base}_{counter}{ext}")):
                        counter += 1
                    local_path = os.path.join(output_dir, f"{base}_{counter}{ext}")
                urllib.request.urlretrieve(img_url, local_path)
                saved_paths.append(local_path)
                print("图片已保存: " + local_path)

    return saved_paths

def main():
    # 加载配置
    config = load_config()
    host = config["comfyui_host"]

    # 获取 prompt
    if len(sys.argv) > 1:
        user_prompt = " ".join(sys.argv[1:])
    else:
        user_prompt = generate_random_prompt(config)
        #print("随机提示词: " + user_prompt)

    print("使用 prompt: " + user_prompt)

    # 检查服务
    print("检查服务...")
    if not check_service(host):
        print("ERROR: ComfyUI 服务不可用")
        sys.exit(1)

    # 构建并提交任务
    print("提交任务...")
    prompt_data = build_prompt(user_prompt, config)
    prompt_id = submit_prompt(host, prompt_data, config["timeout"])
    print("prompt_id: " + str(prompt_id))

    # 等待完成
    outputs, error = wait_for_completion(
        host, prompt_id, config["timeout"], config["poll_interval"]
    )

    if error:
        print("ERROR: " + str(error))
        sys.exit(1)

    # 下载图片
    
    if config["output_dir"]:
        saved_paths = download_images(host, outputs, config["output_dir"])

        if saved_paths:
            print("DONE:" + saved_paths[0])
        else:
            print("ERROR: 未生成图片")
            sys.exit(1)

if __name__ == "__main__":
    main()
