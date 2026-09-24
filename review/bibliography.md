# Bibliography — Stage 1 Distribution-Learning Prior for Diverse Saponin Generation

**Cycle 1, citation-verification pass applied (2026-09-22).**

**Verification status legend**

- ✅ **Verified** — bibliographic metadata (authors, venue, year, identifier) confirmed against the publisher page, the preprint server, an official repository, or the reference list of a primary source fetched in this cycle.
- ⚠️ **Partially verified** — the work and its venue/identifier are confirmed, but part of the metadata (usually the full author list) could not be resolved this cycle. The reason is stated. **No author name in this file is a guess**; where authorship is unknown the entry says so rather than inventing one.

Tooling note: Crossref and Europe PMC metadata APIs rate-limited this session, and PubMed/PMC served CAPTCHA interstitials to the fetch tool, so several entries were resolved via publisher pages, arXiv/bioRxiv, or the reference lists of papers fetched in full.

---

## Primary sources — chemical language models (SMILES / string representations)

1. ✅ **[Skinnider2021]** Skinnider, M. A.; Stacey, R. G.; Wishart, D. S.; Foster, L. J. (2021). *Chemical language models enable navigation in sparsely populated chemical space.* **Nature Machine Intelligence** 3(9), 759–770. DOI: [10.1038/s42256-021-00368-1](https://doi.org/10.1038/s42256-021-00368-1). Full text read this cycle. Code: [github.com/skinnider/low-data-generative-models](https://github.com/skinnider/low-data-generative-models); CLMeval R package: [github.com/skinnider/CLMeval](https://github.com/skinnider/CLMeval); data: [10.5281/zenodo.4641960](https://doi.org/10.5281/zenodo.4641960); code archive: [10.5281/zenodo.4642099](https://doi.org/10.5281/zenodo.4642099).

2. ✅ **[Skinnider2024]** Skinnider, M. A. (2024). *Invalid SMILES are beneficial rather than detrimental to chemical language models.* **Nature Machine Intelligence** 6(4), 437–448. DOI: [10.1038/s42256-024-00821-x](https://doi.org/10.1038/s42256-024-00821-x). Open access.

3. ✅ **[Moret2020]** Moret, M.; Friedrich, L.; Grisoni, F.; Merk, D.; Schneider, G. (2020). *Generative molecular design in low data regimes.* **Nature Machine Intelligence** 2(3), 171–180. DOI: [10.1038/s42256-020-0160-y](https://doi.org/10.1038/s42256-020-0160-y). Code: [github.com/ETHmodlab/virtual_libraries](https://github.com/ETHmodlab/virtual_libraries).

4. ✅ **[Amabilino2020]** Amabilino, S.; Pogány, P.; Pickett, S. D.; Green, D. V. S. (2020). *Guidelines for Recurrent Neural Network Transfer Learning-Based Molecular Generation of Focused Libraries.* **Journal of Chemical Information and Modeling** 60(12), 5699–5713. DOI: [10.1021/acs.jcim.0c00343](https://doi.org/10.1021/acs.jcim.0c00343). PMID: 32659085. Paywalled; Supporting Information free.

5. ✅ **[Loeffler2024]** Loeffler, H. H.; He, J.; Tibo, A.; Janet, J. P.; Voronov, A.; Mervin, L. H.; Engkvist, O. (2024). *REINVENT 4: Modern AI-driven generative molecule design.* **Journal of Cheminformatics** 16, 20. DOI: [10.1186/s13321-024-00812-5](https://doi.org/10.1186/s13321-024-00812-5). PMID: 38383444. Code: [github.com/MolecularAI/REINVENT4](https://github.com/MolecularAI/REINVENT4), **Apache 2.0**. Preprint: [10.26434/chemrxiv-2023-xt65x](https://doi.org/10.26434/chemrxiv-2023-xt65x).

6. ✅ **[Bagal2022]** Bagal, V.; Aggarwal, R.; Vinod, P. K.; Priyakumar, U. D. (2022). *MolGPT: Molecular Generation Using a Transformer-Decoder Model.* **Journal of Chemical Information and Modeling** 62(9), 2064–2076. DOI: [10.1021/acs.jcim.1c00600](https://doi.org/10.1021/acs.jcim.1c00600). PMID: 34694798.

7. ✅ **[Ozcelik2024]** Özçelik, R.; de Ruiter, S.; Criscuolo, E.; Grisoni, F. (2024). *Chemical language modeling with structured state space sequence models.* **Nature Communications** 15(1), 6176. DOI: [10.1038/s41467-024-50469-9](https://doi.org/10.1038/s41467-024-50469-9). PMID: 39039051. Code: [github.com/molML/s4-for-de-novo-drug-design](https://github.com/molML/s4-for-de-novo-drug-design).

8. ✅ **[ArusPous2019]** Arús-Pous, J.; Johansson, S. V.; Prykhodko, O.; Bjerrum, E. J.; Tyrchan, C.; Reymond, J.-L.; Chen, H.; Engkvist, O. (2019). *Randomized SMILES strings improve the quality of molecular generative models.* **Journal of Cheminformatics** 11, 71. DOI: [10.1186/s13321-019-0393-0](https://doi.org/10.1186/s13321-019-0393-0). Confirmed via the reference list of [Skinnider2021].

9. ✅ **[Bjerrum2017]** Bjerrum, E. J. (2017). *SMILES Enumeration as Data Augmentation for Neural Network Modeling of Molecules.* arXiv:[1703.07076](https://arxiv.org/abs/1703.07076). Implementation: [github.com/EBjerrum/SMILES-enumeration](https://github.com/EBjerrum/SMILES-enumeration).

10. ✅ **[ArusPous2020]** Arús-Pous, J.; Patronov, A.; Bjerrum, E. J.; Tyrchan, C.; Reymond, J.-L.; Chen, H.; Engkvist, O. (2020). *SMILES-based deep generative scaffold decorator for de-novo drug design.* **Journal of Cheminformatics** 12, 38. DOI: [10.1186/s13321-020-00441-8](https://doi.org/10.1186/s13321-020-00441-8). PMCID: PMC7260788.

11. ✅ **[Krenn2020]** Krenn, M.; Häse, F.; Nigam, A.; Friederich, P.; Aspuru-Guzik, A. (2020). *Self-referencing embedded strings (SELFIES): A 100% robust molecular string representation.* **Machine Learning: Science and Technology** 1(4), 045024. DOI: [10.1088/2632-2153/aba947](https://doi.org/10.1088/2632-2153/aba947). Code: [github.com/aspuru-guzik-group/selfies](https://github.com/aspuru-guzik-group/selfies).

12. ✅ **[Weininger1988]** Weininger, D. (1988). *SMILES, a chemical language and information system. 1. Introduction to methodology and encoding rules.* **Journal of Chemical Information and Computer Sciences** 28(1), 31–36. DOI: [10.1021/ci00057a005](https://doi.org/10.1021/ci00057a005).

---

## Primary sources — natural-product-specific generative modelling

13. ✅ **[Sakano2024]** Sakano, K.; Furui, K.; Ohue, M. (2024). *NPGPT: Natural Product-Like Compound Generation with GPT-based Chemical Language Models.* arXiv:[2411.12886](https://arxiv.org/abs/2411.12886). Journal version: **The Journal of Supercomputing** 81, article 352 (2025). Code and COCONUT-fine-tuned checkpoints: [github.com/ohuelab/npgpt](https://github.com/ohuelab/npgpt), **MIT licence**.

14. ✅ **[Liu2025]** Liu, C.-S.; Yan, B.-C.; Sun, H.-D.; Lu, J.-C.; Puno, P.-T. (2025). *Bridging chemical space and biological efficacy: advances and challenges in applying generative models in structural modification of natural products.* **Natural Products and Bioprospecting** 15(1), 37. DOI: [10.1007/s13659-025-00521-y](https://doi.org/10.1007/s13659-025-00521-y). PMID: 40478370. Full text read this cycle.

15. ✅ **[Merk2018]** Merk, D.; Grisoni, F.; Friedrich, L.; Schneider, G. (2018). *Tuning artificial intelligence on the de novo design of natural-product-inspired retinoid X receptor modulators.* **Communications Chemistry** 1, 68. DOI: [10.1038/s42004-018-0068-1](https://doi.org/10.1038/s42004-018-0068-1).

16. ✅ **[Zheng2019]** Zheng, S.; Yan, X.; Gu, Q.; Yang, Y.; Du, Y.; Lu, Y.; Xu, J. (2019). *QBMG: quasi-biogenic molecule generator with deep recurrent neural network.* **Journal of Cheminformatics** 11, 5. DOI: [10.1186/s13321-019-0328-9](https://doi.org/10.1186/s13321-019-0328-9). Confirmed via the reference list of [Skinnider2021]. *Not yet read in full — Cycle 2.*

17. ✅ **[Pesciullesi2020]** Pesciullesi, G.; Schwaller, P.; Laino, T.; Reymond, J.-L. (2020). *Transfer learning enables the molecular transformer to predict regio- and stereoselective reactions on carbohydrates.* **Nature Communications** 11(1), 4874. DOI: [10.1038/s41467-020-18671-7](https://doi.org/10.1038/s41467-020-18671-7).

---

## Primary sources — graph-based models (VAE, GAN, flow, autoregressive)

18. ✅ **[Jin2018]** Jin, W.; Barzilay, R.; Jaakkola, T. (2018). *Junction Tree Variational Autoencoder for Molecular Graph Generation.* **Proceedings of the 35th International Conference on Machine Learning (ICML)**, PMLR 80, 2323–2332. arXiv:[1802.04364](https://arxiv.org/abs/1802.04364). Code: [github.com/wengong-jin/icml18-jtnn](https://github.com/wengong-jin/icml18-jtnn); successor: [github.com/wengong-jin/hgraph2graph](https://github.com/wengong-jin/hgraph2graph). Supplementary material (stereochemistry re-ranking procedure) read this cycle.

19. ✅ **[Ochiai2023]** Ochiai, T.; Inukai, T.; Akiyama, M.; Furui, K.; Ohue, M.; Matsumori, N.; Inuki, S.; Uesugi, M.; Sunazuka, T.; Kikuchi, K.; Kakeya, H.; Sakakibara, Y. (2023). *Variational autoencoder-based chemical latent space for large molecular structures with 3D complexity.* **Communications Chemistry** 6(1), 249. DOI: [10.1038/s42004-023-01054-6](https://doi.org/10.1038/s42004-023-01054-6). Author list confirmed via the reference list of [Sakano2024]. **⚠️ Abstract-level only — flagged in `open_questions.md` as the top Cycle 2 read.**

20. ✅ **[DeCao2018]** De Cao, N.; Kipf, T. (2018). *MolGAN: An implicit generative model for small molecular graphs.* **ICML 2018 Deep Generative Models Workshop.** arXiv:[1805.11973](https://arxiv.org/abs/1805.11973). Code: [github.com/nicola-decao/MolGAN](https://github.com/nicola-decao/MolGAN).

21. ⚠️ **[Madhawa2019]** Madhawa, K.; Ishiguro, K.; *et al.* (2019). *GraphNVP: An Invertible Flow Model for Generating Molecular Graphs.* arXiv:[1905.11600](https://arxiv.org/abs/1905.11600). Code: [github.com/pfnet-research/graph-nvp](https://github.com/pfnet-research/graph-nvp) (Preferred Networks Research). **First two authors confirmed** via the Semantic Scholar record; the remaining author names could not be resolved this cycle (arXiv abstract page returned no author block to the fetch tool; dblp disallows fetching). Minor citation — low relevance to the decision.

22. ✅ **[Mercado2020]** Mercado, R.; Rastemo, T.; Lindelöf, E.; Klambauer, G.; Engkvist, O.; Chen, H.; Bjerrum, E. J. (2020). *Practical notes on building molecular graph generative models.* **Applied AI Letters** 1(2), e18. DOI: [10.1002/ail2.18](https://doi.org/10.1002/ail2.18). Confirmed via the reference list of [Skinnider2021]. GraphINVENT code repository availability **⚠️UNVERIFIED**.

23. ✅ **[Subramanian2023]** Subramanian, A.; Greenman, K. P.; Gervaix, A.; Yang, T.; Gómez-Bombarelli, R. (2023). *Automated patent extraction powers generative modeling in focused chemical spaces.* arXiv:[2303.08272](https://arxiv.org/abs/2303.08272). Journal version: **Digital Discovery** 2023, 2, 1006–1015, DOI: [10.1039/D3DD00041A](https://doi.org/10.1039/D3DD00041A) *(journal venue ⚠️ not re-confirmed this cycle; arXiv record verified)*. Table 1 distribution-learning numbers read this cycle.

---

## Primary sources — diffusion models

24. ✅ **[Vignac2023]** Vignac, C.; Krawczuk, I.; Siraudin, A.; Wang, B.; Cevher, V.; Frossard, P. (2023). *DiGress: Discrete Denoising Diffusion for Graph Generation.* **International Conference on Learning Representations (ICLR) 2023.** arXiv:[2209.14734](https://arxiv.org/abs/2209.14734). OpenReview: [UaAD-Nu86WX](https://openreview.net/pdf?id=UaAD-Nu86WX). Code: [github.com/cvignac/DiGress](https://github.com/cvignac/DiGress). Full text read this cycle.

25. ✅ **[Hoogeboom2022]** Hoogeboom, E.; Satorras, V. G.; Vignac, C.; Welling, M. (2022). *Equivariant Diffusion for Molecule Generation in 3D.* **Proceedings of the 39th International Conference on Machine Learning (ICML)**, PMLR 162, 8867–8887. arXiv:[2203.17003](https://arxiv.org/abs/2203.17003).

26. ✅ **[Xu2023]** Xu, M.; Powers, A.; Dror, R.; Ermon, S.; Leskovec, J. (2023). *Geometric Latent Diffusion Models for 3D Molecule Generation.* **Proceedings of the 40th International Conference on Machine Learning (ICML)**, PMLR 202. arXiv:[2305.01140](https://arxiv.org/abs/2305.01140). Author list verified this cycle.

27. ✅ **[Peng2023]** Peng, X.; Guan, J.; Liu, Q.; Ma, J. (2023). *MolDiff: Addressing the Atom-Bond Inconsistency Problem in 3D Molecule Diffusion Generation.* **Proceedings of the 40th International Conference on Machine Learning (ICML)**, PMLR 202, 27611–27629. arXiv:[2305.07508](https://arxiv.org/abs/2305.07508). Code: [github.com/pengxingang/MolDiff](https://github.com/pengxingang/MolDiff).

---

## Benchmarks, metrics and evaluation frameworks

28. ✅ **[Polykovskiy2020]** Polykovskiy, D.; Zhebrak, A.; Sanchez-Lengeling, B.; Golovanov, S.; Tatanov, O.; Belyaev, S.; Kurbanov, R.; Artamonov, A.; Aladinskiy, V.; Veselov, M.; Kadurin, A.; Johansson, S.; Chen, H.; Nikolenko, S.; Aspuru-Guzik, A.; Zhavoronkov, A. (2020). *Molecular Sets (MOSES): A Benchmarking Platform for Molecular Generation Models.* **Frontiers in Pharmacology** 11, 565644. DOI: [10.3389/fphar.2020.565644](https://doi.org/10.3389/fphar.2020.565644). PMID: 33390943. arXiv:[1811.12823](https://arxiv.org/abs/1811.12823). Code: [github.com/molecularsets/moses](https://github.com/molecularsets/moses).

29. ✅ **[Brown2019]** Brown, N.; Fiscato, M.; Segler, M. H. S.; Vaucher, A. C. (2019). *GuacaMol: Benchmarking Models for de Novo Molecular Design.* **Journal of Chemical Information and Modeling** 59(3), 1096–1108. DOI: [10.1021/acs.jcim.8b00839](https://doi.org/10.1021/acs.jcim.8b00839). arXiv:[1811.09621](https://arxiv.org/abs/1811.09621). Code: [github.com/BenevolentAI/guacamol](https://github.com/BenevolentAI/guacamol). Appendix (dataset construction) read this cycle.

30. ✅ **[Thomas2024]** Thomas, M.; O'Boyle, N. M.; Bender, A.; de Graaf, C. (2024). *MolScore: a scoring, evaluation and benchmarking framework for generative models in de novo drug design.* **Journal of Cheminformatics** 16, 64. DOI: [10.1186/s13321-024-00861-w](https://doi.org/10.1186/s13321-024-00861-w). PMCID: PMC11141043. Preprint: [10.26434/chemrxiv-2023-c4867-v2](https://doi.org/10.26434/chemrxiv-2023-c4867-v2). Code: [github.com/MorganCThomas/MolScore](https://github.com/MorganCThomas/MolScore); [PyPI](https://pypi.org/project/MolScore/).

31. ✅ **[Renz2024]** Renz, P.; Luukkonen, S.; Klambauer, G. (2024). *Diverse Hits in De Novo Molecule Design: Diversity-Based Comparison of Goal-Directed Generators.* **Journal of Chemical Information and Modeling** 64(15), 5756–5761. DOI: [10.1021/acs.jcim.4c00519](https://doi.org/10.1021/acs.jcim.4c00519). PMID: 39029090; PMCID: PMC11323242. Workshop version: ICLR 2024 GEM Workshop; data: [Zenodo 11004835](https://zenodo.org/records/11004835). **Authorship verified this cycle — corrects the `[Koch2024]` key used in the first draft of the report.**

32. ✅ **[Preuer2018]** Preuer, K.; Renz, P.; Unterthiner, T.; Hochreiter, S.; Klambauer, G. (2018). *Fréchet ChemNet Distance: A Metric for Generative Models for Molecules in Drug Discovery.* **Journal of Chemical Information and Modeling** 58(9), 1736–1741. DOI: [10.1021/acs.jcim.8b00234](https://doi.org/10.1021/acs.jcim.8b00234). PyTorch implementation: [github.com/insilicomedicine/fcd_torch](https://github.com/insilicomedicine/fcd_torch).

33. ✅ **[Ertl2008]** Ertl, P.; Roggo, S.; Schuffenhauer, A. (2008). *Natural Product-likeness Score and Its Application for Prioritization of Compound Libraries.* **Journal of Chemical Information and Modeling** 48(1), 68–74. DOI: [10.1021/ci700286x](https://doi.org/10.1021/ci700286x).

34. ✅ **[Ertl2009]** Ertl, P.; Schuffenhauer, A. (2009). *Estimation of synthetic accessibility score of drug-like molecules based on molecular complexity and fragment contributions.* **Journal of Cheminformatics** 1, 8. DOI: [10.1186/1758-2946-1-8](https://doi.org/10.1186/1758-2946-1-8).

35. ✅ **[Bemis1996]** Bemis, G. W.; Murcko, M. A. (1996). *The properties of known drugs. 1. Molecular frameworks.* **Journal of Medicinal Chemistry** 39(15), 2887–2893. DOI: [10.1021/jm00015a007](https://doi.org/10.1021/jm00015a007). Confirmed via the reference list of [Skinnider2021].

---

## Databases

36. ✅ **[Chandrasekhar2025]** Chandrasekhar, V.; Rajan, K.; Kanakam, S. R. S.; Sharma, N.; Weißenborn, V.; Schaub, J.; Steinbeck, C. (2025). *COCONUT 2.0: a comprehensive overhaul and curation of the collection of open natural products database.* **Nucleic Acids Research** 53(D1), D634–D643. DOI: [10.1093/nar/gkae1063](https://doi.org/10.1093/nar/gkae1063). PMID: 39588778; PMCID: PMC11701633. Database: [coconut.naturalproducts.net](https://coconut.naturalproducts.net); code: [github.com/Steinbeck-Lab/coconut](https://github.com/Steinbeck-Lab/coconut); bulk data: [Zenodo 13692394](https://zenodo.org/records/13692394).

37a. ✅ **[Zeng2020]** Zeng, T.; Liu, Z.; Zhuang, J.; Jiang, Y.; He, W.; Diao, H.; Lv, N.; Jian, Y.; Liang, D.; Qiu, Y.; Zhang, R.; Zhang, F.; Tang, X.; Wu, R. (2020). *TeroKit: A Database-Driven Web Server for Terpenome Research.* **Journal of Chemical Information and Modeling** 60(4), 2082–2090. DOI: [10.1021/acs.jcim.0c00141](https://doi.org/10.1021/acs.jcim.0c00141). PMID: 32286817. Server: [terokit.qmclab.com](https://terokit.qmclab.com/). **The source of this project's ~40,000-molecule triterpenoid/saponin corpus.** Author list verified this cycle; the per-class molecule breakdown could not be read (ACS returned 403).

37b. ✅ **[Chen2023]** Chen, N.; Zhang, R.; Zeng, T.; Zhang, X.; Wu, R. (2023). *Developing TeroENZ and TeroMAP modules for the terpenome research platform TeroKit.* **Database** 2023, baad020. DOI: [10.1093/database/baad020](https://doi.org/10.1093/database/baad020). PMID: 37207351; PMCID: PMC10380177. Full text read this cycle: TeroMOL contains **~180,000 terpenome molecules** (updated December 2022) spanning mono-, sesqui-, di-, tri- and sesterterpenoids, meroterpenoids and steroids, **including glycosides**; TeroENZ adds 13,462 biosynthetic enzymes across 2,541 species and 4,293 reactions. Bulk data: [terokit.qmclab.com/data.html](http://terokit.qmclab.com/data.html) — all TeroMOL structures as a ~62 MB SMILES text file. **⚠️ Stereochemistry completeness of the bulk download is not documented** (risk R12).

37. ✅ **[Sorokina2021]** Sorokina, M.; Merseburger, P.; Rajan, K.; Yirik, M. A.; Steinbeck, C. (2021). *COCONUT online: Collection of Open Natural Products database.* **Journal of Cheminformatics** 13(1), 2. DOI: [10.1186/s13321-020-00478-9](https://doi.org/10.1186/s13321-020-00478-9). (COCONUT v1; superseded by [Chandrasekhar2025].)

---

## Evaluation methodology and stereochemistry-aware generation (added v3.2 / gap analysis)

46. ✅ **[Ozcelik2025]** Özçelik, R.; Grisoni, F. (2025). *How evaluation choices distort the outcome of generative drug discovery.* **Journal of Cheminformatics** 17, 169. DOI: [10.1186/s13321-025-01108-y](https://doi.org/10.1186/s13321-025-01108-y). PMCID: PMC12613558. Full text read this cycle. Shows that **design-library size systematically biases evaluation and can reverse model rankings**: FCD and FDD decrease with library size, plateauing only above 10⁴–10⁵ designs; **uniqueness decreases as library size increases**, ranking models differently across scales — the authors recommend treating uniqueness as a "sanity check" only. Frequently-generated molecules are often simple substructures (benzene, amine, ether) and "unsuitable for prospective studies". Restrictive top-*k*/top-*p* causes mode collapse while **temperature sampling remains superior** for diversity control. Proposes "number of substructures" as a size-invariant metric ~85× faster than clustering. Recommends reporting similarity metrics only for libraries of ≥10⁵ designs and comparing across libraries of **identical size regardless of architecture**. *Distinct from [Ozcelik2024] (S4 chemical language modelling) — same first author, different paper.*

47. ✅ **[Tom2025]** Tom, G.; Yu, E.; Yoshikawa, N.; Jorner, K.; Aspuru-Guzik, A. (2025). *Stereochemistry-aware string-based molecular generation.* **PNAS Nexus** 4(11), pgaf329. DOI: [10.1093/pnasnexus/pgaf329](https://doi.org/10.1093/pnasnexus/pgaf329). PMID: 41190212; PMCID: PMC12582147. Preprint: [10.26434/chemrxiv-2024-tkjr1](https://doi.org/10.26434/chemrxiv-2024-tkjr1). Code: [github.com/aspuru-guzik-group/stereogeneration](https://github.com/aspuru-guzik-group/stereogeneration). States that current generative models "either ignore stereochemistry or consider it as a postprocessing step after molecule generation" — **the citable confirmation that the field treats stereochemistry as an afterthought**. Evaluates E/Z geometric diastereomers and R/S diastereomers and enantiomers on a ~250,000-molecule ZINC15 subset, using isomeric-ECFP rediscovery similarity, docking scores, circular-dichroism peak scores and optimisation AUC. **Critically for this project, it explicitly excludes axial chirality and ring isomers** — ring-fusion stereochemistry, the feature that defines a triterpenoid aglycone's 3D shape, is outside the scope of the state of the art. This is the basis for the claim that protocol metric S16 has no precedent.

---

## Synthesizability and biosynthesis (added by `evaluation_protocol.md` v3.0)

44. ✅ **[Thakkar2021]** Thakkar, A.; Chadimová, V.; Bjerrum, E. J.; Engkvist, O.; Reymond, J.-L. (2021). *Retrosynthetic accessibility score (RAscore) — rapid machine learned synthesizability classification from AI driven retrosynthetic planning.* **Chemical Science** 12(9), 3339–3349. DOI: [10.1039/D0SC05401A](https://doi.org/10.1039/D0SC05401A). PMID: 34164104; PMCID: PMC8179384. Article CC BY-NC 3.0. An ML classifier for whether a synthetic route can be found, computing **at least 4,500× faster** than the underlying CASP retrosynthesis tool. **⚠️ Not extractable this cycle:** direct comparison against SA score / SCScore, any statement on natural-product performance, code repository location, and applicability-domain caveats. Trained on drug-like retrosynthesis — **validate on real saponins before trusting it** (protocol §9.1).

45. ✅ **[Zheng2022]** Zheng, S.; Zeng, T.; Li, C.; Chen, B.; Coley, C. W.; Yang, Y.; Wu, R. (2022). *Deep learning driven biosynthetic pathways navigation for natural products with BioNavi-NP.* **Nature Communications** 13, 3342. DOI: [10.1038/s41467-022-30970-9](https://doi.org/10.1038/s41467-022-30970-9). PMCID: PMC9187661. Preprint: arXiv:[2105.13121](https://arxiv.org/abs/2105.13121). Code: [github.com/prokia/BioNavi-NP](https://github.com/prokia/BioNavi-NP); server: biopathnavi.qmclab.com. Full text read this cycle: transformer + AND-OR-tree search predicting biosynthetic pathways; **90.2% success on 368 test compounds**, 72.8% building-block recovery (1.7× a rule-based approach), 60.6% single-step top-10, 88% on 25 unseen compounds. Covers terpenoids via the MVA/MEP pathway. **Note the adjacency:** shares authors (Zeng, Wu) and the `qmclab.com` domain with TeroKit [Zeng2020, Chen2023] — the same group that built the project's training database. Interoperability is **⚠️ unverified** but is the first thing to check. Glycosides are not called out as a distinct pathway category.

---

## Chemical ontology classification (added by `evaluation_protocol.md` v2.0)

42. ✅ **[Kim2021]** Kim, H. W.; Wang, M.; Leber, C. A.; Nothias, L.-F.; Reher, R.; Kang, K. B.; van der Hooft, J. J. J.; Dorrestein, P. C.; Gerwick, W. H.; Cottrell, G. W. (2021). *NPClassifier: A Deep Neural Network-Based Structural Classification Tool for Natural Products.* **Journal of Natural Products** 84(11), 2795–2807. DOI: [10.1021/acs.jnatprod.1c00399](https://doi.org/10.1021/acs.jnatprod.1c00399). PMID: 34662515. Code: [github.com/mwang87/NP-Classifier](https://github.com/mwang87/NP-Classifier) — **MIT licence for code; data, models and ontology CC0**. API: `/classify?smiles=<>` (plus a `cached` flag and a `/model/metadata` endpoint); returns a three-level pathway → superclass → class ontology and an **`isglycoside`** flag. Dockerised for local deployment; live service at npclassifier.gnps2.org. Author list, venue and repository details verified this cycle. **⚠️ Not extractable this cycle:** the exact number of categories per ontology level, per-class accuracy/F1, and how the classifier weighs aglycone versus sugar contributions — ACS returned 403 and PMC served CAPTCHA pages. Validate on your own reference set before gating on class-level metrics (protocol §6.1).

43. ✅ **[Djoumbou2016]** Djoumbou Feunang, Y.; Eisner, R.; Knox, C.; Chepelev, L.; Hastings, J.; Owen, G.; Fahy, E.; Steinbeck, C.; Subramanian, S.; Bolton, E.; Greiner, R.; Wishart, D. S. (2016). *ClassyFire: automated chemical classification with a comprehensive, computable taxonomy.* **Journal of Cheminformatics** 8, 61. DOI: [10.1186/s13321-016-0174-y](https://doi.org/10.1186/s13321-016-0174-y). Author list and taxonomy statistics verified this cycle: the ChemOnt taxonomy holds **4,825 categories** (4,146 organic, 678 inorganic) plus a root, up to **11 levels** deep, averaging five levels per node. Used in the protocol as a secondary cross-check on [Kim2021], not as the primary classifier — it is general-purpose rather than natural-product-native.

---

## Optimisation and evaluation of priors (added by `evaluation_protocol.md`)

40. ✅ **[Gao2022]** Gao, W.; Fu, T.; Sun, J.; Coley, C. W. (2022). *Sample Efficiency Matters: A Benchmark for Practical Molecular Optimization.* **NeurIPS 2022, Datasets and Benchmarks Track**. Code: [github.com/wenhao-gao/mol_opt](https://github.com/wenhao-gao/mol_opt). Full text read this cycle: 25 algorithms across 23 single-objective tasks, scored by AUC of top-10 average property value vs number of oracle calls (min-max scaled, 10,000-call budget). **REINVENT ranked first overall for sample efficiency**; Graph GA second; SMILES LSTM-HC sixth. Source for the T4.3 sample-efficiency probe.

41. ✅ **[Guo2024]** Guo, J.; Schwaller, P. (2024). *Augmented Memory: Sample-Efficient Generative Molecular Design with Reinforcement Learning.* **JACS Au** 4(6), 2160–2172. DOI: [10.1021/jacsau.4c00066](https://doi.org/10.1021/jacsau.4c00066). PMCID: PMC11200228. Full text read this cycle. **Source for the key mechanism in the evaluation protocol**: the prior-likelihood term sits inside the Stage 2 RL loss and "acts to ensure that the generated SMILES are syntactically valid and has been shown to empirically enforce reasonable chemistry" — so prior quality bounds Stage 2 output. Also documents RL mode collapse and its detection. Reports 15.002 AUC top-10 on PMO vs REINVENT's 14.016.

---

## Glycan- and carbohydrate-specific sources

38. ✅ **[SweetFold2026]** Sundar, K.; Yang, H. (2026). *A Glycan-Aware Diffusion Model for Carbohydrate and Glycoprotein Structure Prediction.* **bioRxiv** preprint. DOI: [10.64898/2026.07.16.738959](https://doi.org/10.64898/2026.07.16.738959). PMCID: PMC13404910; PMID: 42523330. Also on [Zenodo 21105358](https://zenodo.org/records/21105358). Authorship and the "context dilution" / sugar-collapse mechanism verified this cycle via the bioRxiv record. **Note:** a structure-prediction model, not a generative one — cited in this review for its representational analysis, not its generative results.

39. ⚠️ **[CarbCofolding2026]** *Physical Implausibility of Carbohydrate Ligands in Results of Deep Learning-Based Cofolding Methods.* (2026). **Journal of Chemical Information and Modeling** 66(7), 3456. PMID: 41866819; PMCID: PMC13080964. Publisher page: [pubs.acs.org/jcisd8/article/66/7/3456](https://pubs.acs.org/jcisd8/article/66/7/3456/5138336/Physical-Implausibility-of-Carbohydrate-Ligands-in). **Author list could not be resolved this cycle** — ACS returned HTTP 403, PMC/PubMed served CAPTCHA pages, and the Crossref and Europe PMC APIs rate-limited. The key is therefore topic-based rather than author-based. Venue, volume, issue, page and both identifiers are confirmed; the substantive finding (systematic glycan stereochemistry errors across canonical-SMILES input variants in AlphaFold3 and Boltz-1x) was read from an indexed excerpt, **not the full text**. Re-resolve in Cycle 2 before relying on it in any write-up.

---

## Secondary sources consulted (leads only — not cited for factual claims)

- ✅ **[Ozcelik2025]** Özçelik, R.; Brinkmann, H.; Criscuolo, E.; Grisoni, F. (2025). *Generative Deep Learning for de Novo Drug Design — A Chemical Space Odyssey.* **Journal of Chemical Information and Modeling**. DOI: [10.1021/acs.jcim.5c00641](https://doi.org/10.1021/acs.jcim.5c00641). PMCID: PMC12308806. *Perspective; flagged in `open_questions.md` as a Cycle 2 read.*
- ✅ **[vanTilborg2024]** van Tilborg, D.; Brinkmann, H.; Criscuolo, E.; Rossen, L.; Özçelik, R.; Grisoni, F. (2024). *Deep learning for low-data drug discovery: Hurdles and opportunities.* **Current Opinion in Structural Biology**. *Directly on-topic for the low-data question; flagged as a Cycle 2 read.*
- [AspirinCode] *papers-for-molecular-design-using-DL* — curated list, [github.com/AspirinCode/papers-for-molecular-design-using-DL](https://github.com/AspirinCode/papers-for-molecular-design-using-DL). Used only to surface candidate primary sources.
- *Computational Chemistry Highlights* commentary on [Skinnider2024] — used only to locate the primary source.

---

## Sources consulted and found **not** relevant to Stage 1

Recorded so later cycles do not re-search them:

- Prediction of Hemolytic Toxicity for Saponins by Machine-Learning Methods — **JCIM/Chem. Res. Toxicol. 2019**, DOI: [10.1021/acs.chemrestox.8b00347](https://doi.org/10.1021/acs.chemrestox.8b00347). A *classification* model over 331 hemolytic / 121 non-hemolytic saponins, not a generative model. **Potentially valuable as a Stage 2 scoring function**, and as evidence that a curated saponin set of this size exists in the literature — but not a Stage 1 prior.
- Machine Learning-Based Analysis Reveals Triterpene Saponins … AMPK Activation — **Pharmaceutics 2024**, DOI: [10.3390/pharmaceutics16040511](https://doi.org/10.3390/pharmaceutics16040511). Classification of 95 constituents; not generative.
- In Silico Studies on Triterpenoid Saponins Permeation through the Blood–Brain Barrier — **IJMS 2020**, PMCID: PMC7177733. QSAR on 47 compounds; not generative.
