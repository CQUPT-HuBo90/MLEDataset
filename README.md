---
tags:
- image-quality
- low-light
- enhancement
---

# QoMEX 2026-Low-light Enhanced Image Quality Assessment Challenge

## Challenge Introduction

In real-world shooting scenarios, particularly in low-light environments such as dimly lit indoor spaces or nighttime streets, images captured by ordinary cameras often face numerous issues. The most prominent problem is the excessive noise that fills the image, severely disrupting its clarity and visual quality. At the same time, image details are extremely lacking, with originally rich textures and key information, such as object contours, becoming blurred, posing significant challenges in fields like nighttime surveillance and driving assistance systems. To overcome this challenge, various Low-light Image Enhancement Algorithms (LIEAs) have been proposed by researchers in recent years. These algorithms aim to improve the quality of images taken in low-light conditions to better meet the needs of practical applications. However, further research reveals that most LIEAs primarily focus on improving brightness and contrast during their design. While it enhances the image’s brightness and color depth to some extent, it also introduces a series of new problems. Therefore, the quality evaluation of Enhanced Low-light Images (ELIs) is particularly important and urgently needed.

To address this challenge, we introduce the Multi-annotated and multimodal Low light image Enhancement (MLE) dataset. This dataset consists of 1000 ELIs, which were obtained by applying 10 LIEAs to 100 low-light images. Each image has been meticulously annotated by subjective studies to obtain multiple attribute annotations (light, color, noise, exposure, nature, and content recovery), quality scores, and textual descriptions. After preliminary research, we have recognized the complexity and challenges of low-light enhanced image quality assessment.

Based on this, we are now launching an open competition, inviting researchers and practitioners to evaluate their models on the publicly released dataset we have made available, and to contribute to advancing the frontiers of multimodal low-light enhanced image quality assessment.

## Challenge Significance

The purpose of holding this challenge is not only to fill the gap in the current field of low-light image processing where there is a lack of authoritative and comprehensive evaluation systems, but also to accelerate the innovation and application of low-light enhancement technology by gathering the wisdom and strength of global researchers, promote the development of evaluation standards that combine subjective perception and objective indicators, thereby significantly improving the visual quality of images in low-light environments, and bringing revolutionary visual experience enhancements to multiple fields such as intelligent security, night photography, and autonomous driving.

## Submission Requirements

1. Download data of MLE, you will find:

   + MLE folder: Image inputs for your model
   + MLE-training.json: Contains six image attributes, MOS value, description, and other parameters for 800 training images. A single sample example is shown below:
   
     ```json5
     [
       {
       "id":"b_1_A",
       "file":"MLE\/data\/b_1_A.png",
       "mos":1.0,  // Mean Opinion Score, overall image quality (0–10)
       "light":1.0,  // Brightness performance (1–5)
       "color":1.0,  // Color fidelity and vividness (1–5).
       "noise":1.0,  // Noise suppression level (1–5)
       "exposure":1.0,  // Exposure balance (1–5)
       "nature":1.0,  // Natural appearance (1–5)
       "content_recovery":1.0,  // Detail restoration in dark areas (1–5)
       "description": "The image..."  // Description of image
       }
     ]
     ```
   + MLE-test.json: Contains 200 samples for contestants to evaluate and submit results. A single sample example is shown below:

     ```json5
     [
       {
       "id":"b_1_B",
       "file":" MLE\/data\/b_1_B.png"
       }
     ]
     ```
2. Submit your evaluation result. The submitted file should be named result.json. Your model's predicted results must strictly follow the example structure below:

    ```json5
    [
      {
        "id":"b_1_B",
        "mos":1.0
      }
    ]
    
    ```
   
## Evaluation

The evaluation consists of comparing model predictions with ground truth annotations. Spearman Rank-order Correlation Coefficient (SRCC) and Pearson Linear Correlation Coefficient (PLCC) are the key indicators for ranking the performance of the models. The final ranking will be based on the average value of the two. Under the same numerical conditions, SRCC takes precedence.

## Important dates

+ **2026.01.15** Grand Challenge Start (Release of Training Data, etc.)
+ **2026.03.15** Test data (Input Only) released
+ **2026.03.22** Grand Challenge Submission (Test Output, Code, Fact Sheet)
+ **2026.04.01** Initial Results Release
+ **2026.04.17** Deadline for challenge paper submission
+ **2026.06.29-2026.07.03** Winners Announced

## Organizers’ contacts and short bios

+ Organizer-1

    **Name**: Bo Hu
    
    **Unit/Institution**: Chongqing University of Posts and Telecommunications
    
    **Email**: hubo90@cqupt.edu.cn
    
    **Homepage**: https://faculty.cqupt.edu.cn/hubo1/zh_CN/index.htm
    
    **Introduction**: Bo Hu is an associate professor and doctoral supervisor at the School of Artificial Intelligence, Chongqing University of Posts and Telecommunications. He obtained his bachelor's degree from China University of Mining and Technology in 2014 and his doctoral degree from the same university in 2020. His main research fields include image/video quality assessment and enhancement. In recent years, he has conducted fruitful research in the areas of image/video quality assessment and quality enhancement. He has published over 50 papers in internationally renowned journals and conferences (such as IEEE TIP, TMM, TCSVT, ACM MM, ICME). His innovative contributions have been successfully applied in fields such as intelligent mines. Currently, Bo Hu is a reviewer for several academic journals and conferences, including IEEE TIP, TMM, TCSVT, ACM MM, and ICME.
+ Organizer-2

    **Name**: Haitian Zhao

    **Unit/Institution**: Chongqing University of Posts and Telecommunications

    **Email**: s250331047@stu.cqupt.edu.cn

    **Homepage**: https://github.com/sgpublic
+ Organizer-3

    **Name**: Yuanyuan Hu

    **Unit/Institution**: Chongqing University of Posts and Telecommunications

    **Email**: s230231040@stu.cqupt.edu.cn 
+ Organizer-4

    **Name**: Xinbo Gao

    **Unit/Institution**: Xidian University

    **Email**: xbgao@mail.xidian.edu.cn

    **Homepage**: https://see.xidian.edu.cn/faculty/xbgao/

    **Introduction**: Xinbo Gao (M'02-SM'07-F'24) earned his B.Eng. degree in Electronic Engineering (1994), followed by M.Sc. (1997) and Ph.D. (1999) degrees in Signal and Information Processing, all from Xidian University, Xi'an, China. From 1997 to 1998, he was a research fellow in the Department of Computer Science at Shizuoka University, Shizuoka, Japan. During 2000-2001, he served as a post-doctoral research fellow in the Department of Information Engineering at the Chinese University of Hong Kong, Hong Kong. Since 1999, he has been affiliated with Xidian University's School of Electronic Engineering, where he currently holds the position of Full Professor in Pattern Recognition and Intelligent Systems. Additionally, since 2020, he has been appointed as a Professor of Computer Science and Technology at Chongqing University of Posts and Telecommunications. His research focuses on computer vision, machine learning, and pattern recognition. With over 300 peer-reviewed publications and seven academic books to his credit, Prof. Gao serves on the editorial boards of several prestigious journals including Signal Processing (Elsevier) and Neurocomputing (Elsevier). He has chaired or participated in program committees for approximately 30 international conferences. Prof. Gao is a Fellow of multiple professional societies: IEEE, IET, AAIA, CIE, CCF, and CAAI.
