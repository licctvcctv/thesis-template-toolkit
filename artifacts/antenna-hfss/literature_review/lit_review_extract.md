**文献综述**

**一、多频段手机天线研究背景与频段需求**

随着智能手机承担蜂窝通信、无线局域网、短距离互联、定位与多媒体数据业务，终端天线已经从单一频点的射频部件转向多频段、多天线和整机协同设计对象。IEEE天线术语标准对增益、方向性、极化、输入阻抗等概念作出统一界定，为评价不同天线方案提供了基本术语基础^\[1\]^。Balanis从电磁辐射、阻抗匹配、方向图和阵列理论等方面系统阐述了天线分析方法，其中S参数、辐射效率和方向特性是终端天线设计必须综合考虑的核心指标^\[2\]^。在手机空间高度受限、周边金属器件密集、用户握持环境复杂的条件下，仅依靠单个中心频点匹配已经难以满足实际通信需求。

从频段需求看，5G NR与WLAN共同推动手机天线向宽频和多频融合发展。3GPP TS
38.104中，n78频段对应3.3～3.8 GHz的TDD工作范围，是Sub-6
GHz终端设计中常被重点考察的中频段^\[3\]^。同时，2.4 GHz与5.8 GHz
WLAN频段仍是手机无线连接的重要组成部分，二者与n78频段在频率间隔、电流路径长度和耦合敏感性方面存在明显差异。因此，多频段手机天线的研究重点不只是"在多个频点出现谐振"，而是要在有限净空内使不同频段均达到可用阻抗匹配，并兼顾结构可实现性、隔离度、效率和安全约束。

**二、手机天线与PIFA结构研究基础**

手机天线的发展与平面天线、小型化天线和终端地板耦合理论密切相关。Wong对平面天线在无线通信中的典型结构、宽带化方法和移动终端集成方式进行了系统梳理，说明印刷天线、缝隙天线和PIFA结构因低剖面、易集成和便于加工而广泛用于便携式设备^\[4\]^。PIFA通过馈电点、短路点、辐射枝节和接地板之间的耦合形成近似四分之一波长谐振，相比外置天线更适合嵌入手机内部，但其带宽通常受限，且对馈电位置、短路位置、枝节长度和净空区域变化较敏感。

近年研究表明，终端天线不宜脱离整机地板单独评价。手机地板、边框和周边金属结构会参与电流分布，改变谐振频率和辐射方向图。对于以HFSS等三维全波软件开展的本科毕业设计而言，PIFA仍是较适合的基础结构：一方面，其电流路径清楚，便于解释尺寸变化与谐振频率之间的关系；另一方面，它可以通过折叠枝节、开槽、寄生枝节或地板耦合扩展工作频带。由此可见，本文围绕"手机地板+主PIFA辐射枝节+寄生枝节"的建模路线具有较明确的理论依据和工程可解释性。

**三、5G Sub-6 GHz手机多天线研究现状**

（一）多端口手机MIMO天线研究

5G手机终端通常需要多天线协同工作，因此多端口MIMO结构成为近年研究热点。Huang等设计了一种基于开口谐振环的小型八端口天线阵列，面向5G
Sub-6
GHz手机应用，在有限空间中通过谐振结构压缩天线尺寸，并关注端口隔离和多天线性能^\[5\]^。该文的价值在于说明小型化并不是单纯缩短金属长度，而是通过引入可控谐振单元改变电流分布，为小净空手机天线提供了结构压缩思路。

Sufyan等提出面向5G智能手机的双频独立可调八单元MIMO天线，在地板开槽与探针结构配合下，实现3.5
GHz和4.7
GHz两个频段的相对独立调节^\[6\]^。该研究强调"双频独立可调"的设计目标，即不同频段不应因一个参数变化而完全相互牵制。Lin等则提出基于多模的六端口双频MIMO天线，通过改进L形贴片、地板槽和短枝节共同激励多个模式，覆盖n78、n79以及LTE
Band
46相关频段^\[7\]^。这些研究共同说明，手机多频段设计常依赖多电流路径和多模式耦合，而不是依靠单一辐射臂完成全部频段匹配。

（二）多频段与5G/WLAN融合研究

面向5G与WLAN并存的终端环境，宽频和双宽带设计逐渐成为重要方向。Shen等提出八单元双宽带MIMO天线，用于5G与WLAN通信，其单元由辐射体、馈线和缺陷地结构组成，并通过L形、U形分支与地板扰动改善频带覆盖和隔离度^\[8\]^。该文直接对应5G/WLAN协同覆盖问题，对于本文同时考虑WLAN
2.4 GHz、5G n78和WLAN 5.8 GHz具有参考意义。

Salamin和Hussain提出一种支持Sub-6
GHz频谱的宽带四端口MIMO天线，重点解决移动终端中宽阻抗带宽和多端口布局之间的矛盾^\[9\]^。Bellekhiri等面向5G手机应用设计并分析了高增益Sub-6
GHz天线阵列，强调阵列增益、方向图和终端应用场景之间的关系^\[10\]^。从这些研究可以看出，当前国外研究往往把手机天线放在系统层面讨论，即除S11外，还同时关注隔离度、增益、效率和MIMO多样性指标。与之相比，本文的研究规模较小，但可借鉴其"先明确目标频段，再围绕结构参数和评价指标逐步优化"的写作与仿真逻辑。

**四、仿真建模与智能优化方法研究**

手机天线设计高度依赖三维电磁仿真。传统设计流程通常先根据四分之一波长、电流路径和馈电耦合估算初始结构，再借助HFSS等全波仿真软件进行扫频、参数扫描和报告导出，最后结合S11、VSWR、输入阻抗和方向图判断方案优劣。近年来，随着参数维度增加，部分研究开始引入智能优化和数据驱动方法。Ahmed等提出面向5G智能手机Sub-6
GHz
MIMO天线设计的深度学习方法，尝试利用学习模型加速结构参数到天线性能之间的映射^\[11\]^。该研究说明，当结构参数较多时，单纯人工试凑会变得低效，数据驱动方法可为参数筛选提供辅助。

Sellak等针对Sub-6 GHz
5G应用中的紧凑PIFA天线，提出基于聚类的ANFIS模型，用于分析、综合并改进PIFA设计过程^\[12\]^。该文与本文主题关联较强，因为它直接以PIFA为对象，关注紧凑结构在5G频段下的参数优化问题。Benghanem等研究可重构双单元MIMO天线，使其适用于认知无线电和5G
NR Sub-6
GHz场景^\[13\]^。可重构设计通过改变结构或电路状态提升频段适配能力，但对本科仿真设计而言会引入额外的器件模型和控制机制。因此，本文选择不加入复杂可重构器件，而是在固定PIFA结构中利用主枝节、地板和寄生枝节调节多频响应，是更可控也更容易验证的路线。

**五、隔离度、效率与安全约束研究**

在多天线系统中，端口间隔离度和无用频段抑制同样重要。Rizvi等提出一种紧凑双端口MIMO天线，通过辐射零点实现带外抑制，改善5G
Sub-6
GHz应用中的相邻端口耦合和非目标频段响应^\[14\]^。Salehi和Oraizi提出基于超表面的4T4R
MIMO天线，在Sub-6
GHz范围内获得宽带、高增益和较高端口隔离^\[15\]^。这些研究提示，在实际终端设计中，满足目标频段S11门限只是基础要求，若要进一步面向工程应用，还需要评价端口隔离、效率、方向图稳定性以及带外辐射问题。

工程实现还要求结构简单、成本可控并符合人体电磁暴露约束。Jiang等提出一种简单、低成本、易集成的Sub-6
GHz
MIMO天线方案，强调手机终端天线不仅要追求性能指标，也要考虑制造和集成便利性^\[16\]^。Turgut和Korunur
Engiz在Sub-6
GHz大规模MIMO天线设计中引入信赖域优化框架，并对SAR进行评价，说明电磁暴露安全已经成为5G终端和近人体无线设备研究中的重要约束^\[17\]^。本文目前主要围绕S11、VSWR、输入阻抗和增益图展开，尚未深入计算SAR和总效率，但在研究述评中需要承认这一局限，并把效率、安全和实物测试作为后续改进方向。

**六、研究述评**

综合上述文献可以看出，多频段手机天线研究已经形成较清晰的发展脉络：基础理论层面以天线参数、平面天线和PIFA小型化为支撑；应用需求层面由5G
NR、WLAN和多业务共存推动终端天线向多频段、宽频带和多端口方向发展；设计方法层面则由传统参数扫描逐步扩展到多模激励、地板开槽、寄生枝节、缺陷地结构、智能优化和可重构设计等多种路线。多数近年文献已不再只讨论单一频点最低S11，而是强调频段覆盖、端口隔离、效率、方向图和集成可行性的综合平衡。

现有研究也存在与本文选题相关的不足。第一，许多高水平成果集中在八端口或更多端口的MIMO阵列，结构复杂、参数多，直接迁移到本科HFSS单模型设计中难度较大。第二，部分研究主要服务n77、n78或n79等5G频段，对WLAN
2.4 GHz、5.8 GHz与5G
n78同时覆盖的解释不够集中。第三，智能优化和可重构方法虽然先进，但需要较多样本、器件模型或实验验证，对于以仿真建模和结果分析为主的毕业论文而言，容易造成实现负担。第四，不少文献给出最终结构和性能指标，但对中间参数筛选、失败方案对比和曲线变化原因说明不足。

基于此，本文"多频段手机天线的仿真研究与设计"可在已有研究基础上选择更适合本科论文的切入点：以PIFA为基础结构，以手机地板、馈电点、短路点、主辐射枝节和右侧寄生枝节为主要变量，在HFSS中对2.4～2.5
GHz、3.3～3.8 GHz和5.725～5.85
GHz三个目标频段进行统一扫频验证。相较于复杂MIMO阵列，本文重点体现多频段目标、结构机理和参数对比过程；相较于单一n78仿真，本文通过三段频率的最差S11、VSWR和输入阻抗分析，更能支撑"多频段手机天线"的题目要求。后续若继续深化，可增加辐射效率、总效率、SAR、握持影响和实物测试内容，使仿真结论进一步接近真实终端工程场景。

**参考文献**

\[1\] IEEE Antennas and Propagation Society. IEEE Standard for
Definitions of Terms for Antennas: IEEE Std 145-2025\[S\]. New York:
IEEE, 2025.

\[2\] Balanis C A. Antenna Theory: Analysis and Design\[M\]. 4th ed.
Hoboken: John Wiley & Sons, 2016.

\[3\] 3GPP. NR; Base Station (BS) radio transmission and reception: 3GPP
TS 38.104 V19.4.0\[S\]. Release 19, 2026.

\[4\] Wong K L. Planar Antennas for Wireless Communications\[M\].
Hoboken: John Wiley & Sons, 2003.

\[5\] Huang J, Shen L, Xiao S, Shi X, Liu G. A Miniature Eight-Port
Antenna Array Based on Split-Ring Resonators for 5G Sub-6 GHz Handset
Applications\[J\]. Sensors, 2023, 23(24): 9734. DOI: 10.3390/s23249734.

\[6\] Sufyan A, Khan K B, Zhang X, Siddiqui T A, Aziz A. Dual-band
independently tunable 8-element MIMO antenna for 5G smartphones\[J\].
Heliyon, 2024, 10(4): e25712. DOI: 10.1016/j.heliyon.2024.e25712.

\[7\] Lin H, Sun W, Wang Z, Nie W. A Dual-Band MIMO Antenna Based on
Multimode for 5G Smartphone Applications\[J\]. Progress In
Electromagnetics Research C, 2024, 148: 31-42. DOI:
10.2528/PIERC24071101.

\[8\] Shen L, Huang J, Li Q, Loh T H, Liu G. Dual-Wideband MIMO Antenna
with eight elements for 5G and WLAN communication\[J\]. Progress In
Electromagnetics Research C, 2024, 144: 65-74. DOI:
10.2528/PIERC24021401.

\[9\] Salamin M A, Hussain N. A wideband 4-port MIMO antenna supporting
sub-6 GHz spectrum for 5G mobile terminals\[J\]. Frequenz, 2022,
76(1-2): 45-54. DOI: 10.1515/freq-2021-0070.

\[10\] Bellekhiri A, Chahboun N, Zbitou J, Oukaira A, Laaziz Y. Design
and analysis of a Sub-6 GHz antenna array with high gain for 5G mobile
phone applications\[J\]. International Journal of Electrical and
Computer Engineering, 2024, 14(6): 6401-6410. DOI:
10.11591/ijece.v14i6.pp6401-6410.

\[11\] Ahmed H, Zeng X, Bello H, Wang Y, Iqbal N. Sub-6 GHz MIMO antenna
design for 5G smartphones: A deep learning approach\[J\]. AEU -
International Journal of Electronics and Communications, 2023, 168:
154716. DOI: 10.1016/j.aeue.2023.154716.

\[12\] Sellak L, Khabba A, Amadid J, Chabaa S, Ibnyaich S, Baddou A.
Clustering-based ANFIS model for analyzing, synthesizing, and improving
the design process of a compact PIFA antenna for sub-6 GHz 5G wireless
applications\[J\]. Engineering Research Express, 2025, 7(3): 035353.
DOI: 10.1088/2631-8695/adfac8.

\[13\] Benghanem Y, Mansoul A, Mouffok L. Frequency reconfigurable
two-element MIMO antenna for cognitive radio and 5G new radio sub-6 GHz
applications\[J\]. International Journal of Microwave and Wireless
Technologies, 2024, 16(2): 295-305. DOI: 10.1017/S1759078723001289.

\[14\] Rizvi S N R, Abu Sufian M, Awan W A, Choi Y, Hussain N, Kim N. A
closely spaced two-port MIMO antenna with a radiation null for
out-of-band suppressions for 5G Sub-6 GHz applications\[J\]. PLOS ONE,
2024, 19(7): e0306446. DOI: 10.1371/journal.pone.0306446.

\[15\] Salehi M, Oraizi H. Wideband high gain metasurface-based 4T4R
MIMO antenna with highly isolated ports for sub-6 GHz 5G
applications\[J\]. Scientific Reports, 2024, 14: 15127. DOI:
10.1038/s41598-024-65135-9.

\[16\] Jiang Y, Rafique U, Kiyani A, Shirvanimoghaddam M, Abbas S M. A
Simple and Low-Cost Integratable MIMO Antenna for 5G Sub-6GHz
Applications\[C\]//2023 IEEE International Symposium on Antennas and
Propagation. IEEE, 2023: 1-2. DOI: 10.1109/ISAP57493.2023.10388838.

\[17\] Turgut A, Korunur Engiz B. Trust region framework-based design of
sub-6 GHz m-MIMO antenna and evaluation of SAR\[J\]. COMPEL - The
international journal for computation and mathematics in electrical and
electronic engineering, 2024, 43(3): 669-690. DOI:
10.1108/COMPEL-11-2023-0596.
