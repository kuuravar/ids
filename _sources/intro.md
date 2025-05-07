# Data Science Mini-Project

version 2025-05-07

## Introduction

This is a Data Science Mini-Project aimed at analyzing municipal migration in Finland during the years 1990-2023.

The aim is to study the migration patterns between municipalities, how they have evolved over the years, and possibly reveal the factors underlying migration decisions and/or predict future migrations.

The target group includes municipality and government officials, urbanization planners, or people interested in moving to another municipality.

The project could yield better understanding of medium-to-large-scale social behavior in Finland and help elucidate intervention targets for increasing municipality attractiveness.

The initial hypotheses include:
* People tend to move to and from the bigger cities (urbanization).
* Females move more frequently and further (education).
* When normalized by municipality population, some smaller municipalities experience larger net migration than the largest municipalities.

Questions to answer:
* Which municipality characteristics are correlated with in- and out-migration?
* Are there communities formed between municipalities?
* Can we model the migration as time series? Can we explain what affects the predictions?

The project is documented from start to finish on this current page.
The full details of the analyses and modelling can be found from the notebooks in the menu, but beware that the notebooks are not polished.

At the final stages of the project we realized that normalized net migration would have been more interesting than absolute arrival and departure numbers.
Accordingly, the TFT and LightGBM models are fit on the normalized net migration.

Another important thing to mention, is that the analyses and the models do not include data on migration from or to the other countries.
Also, there is no data included for people born or diseased.
Together, these could have an important effect on normalizing migration flows, but since we restrict the analyses to municipalities with at least 10000 inhabitants the error should hopefully be tolerable.

We start with  Data Collection and Preprocessing, Exploratory Data Analysis, move to Community Detection, and then Modeling.
Conclusions wraps up the document.

The project is done in the Python ecosystem.

Note that the figures can be enlarged by clicking.

## Data Collection and Preprocessing

The used data is open and was collected from Statistics Finland (Tilastokeskus, TK) and Sotkanet.
TK provides the yearly migration data and key municipality statistics, as well as the dwelling price data.
Sotkanet combines data from multiple sources, including Finnish Institute for Health and Welfare (THL).
Statistics Finland has a custom PxWeb API, and Sotkanet a REST API.

Geographic data is accessed through ``geopy`` Python package.

Raw data is stored as CSV files which is enough for the scope of the project.


## Exploratory Data Analysis

### Missing values and preprocessing

We begin with loading the migration and municipality data. 
Then we print a few rows and check for missing values, and datatypes of the dataframe columns.

For municipality statistics, we have 43 features, 10 of which have missing values for 2024.
The year 2024 is discarded.

There are 89 municipalities with population exceeding 10000 each year.
We limit further analyses and modeling on these.

Migration data has no missing values, and reports migration stratified by ``male`` and ``female``.
The migration is comprised of ``Arrival`` and ``Departure`` counts between the municipalities per year.

Migration and municipality statistic data was merged without problems.
Some of the distributions were plotted in the analyses below, and municipalities grouped by the feature values in the PCA analysis as shown later.

For Sotkanet data, it turned out that there were many missing values such that, for all the indicators, some municipalites had no values at all.
We therefore decided to drop the Sotkanet data altogether, apart from the correlation analysis.
It might be possible to get aggregated data based on the larger areas that the municipalities belong to, but is out of scope of the project.


### Sotkanet data correlations

Ten indicators from Sotkanet database were selected somewhat arbitrarily, based on the general knowledge preconception of possibly having an effect on migrations. The indicators were


| ID   | Description                                                                                   |
|-------|----------------------------------------------------------------------------------------------|
| 180   | Measure of educational level                                                                 |
| 181   | Unemployed people, as % of labour force                                                      |
| 289   | Heavy drinking at least once a month, as % of all pupils in 8th and 9th year of comprehensive school |
| 306   | Disability pension recipients aged 25-64, as % of total population of the same age            |
| 493   | Social assistance, recipient persons during year, as % of total population                    |
| 3105  | Alcohol mortality per 100 000 inhabitant                                                     |
| 3169  | Parturients who smoked during pregnancy, % of parturients                                    |
| 3113  | Offences against life and health recorded by the police per 1000 inhabitants                 |
| 3071  | Persons who are difficult to employ (structural unemployment), as % of persons aged 15 - 64   |
| 3076  | Voting turnout in municipal elections, %                                                     |

The correlations of Sotkanet features is shown in {numref}`Fig. {number}<sotka-corr-fig>`.
Some of the correlations are quite strong, but in general the absolute value is below 0.9.
Well known sosioeconomic phenomena can be observed, such as the protective effect of education against the heavy alcohol use.


```{figure} ./images/sotka_corr.png
---
width: 600px
name: sotka-corr-fig
---
The (linear) correlations of the selected Sotkanet indicators for the Finnish municipalities.
```


### Correlations of migration and municipality statistics

Correlations (linear) were analysed between migration and municipality statistics.
We performed correlation analysis separately for males, females, on arrival and departure  municipalities.
We also checked the correlation of differences between arrival and departure municipality statistics and the migration. 
The results were similar for all cases, and we present only correlations for males and arrival municipality statistics.
<!--- To keep the report concise, the raw distributions of the municipality statistics are not shown, but are addressed later in the PCA analysis. -->

In the figure {numref}`Fig. {number}<males-mun-stats-corr-fig>` we see that the features naturally correlate.
Especially the features based on counting are correlated positively, like ``Finnish speakers`` and ``Persons born abroad``.
This is something to keep in mind going further.
For the share-based features, the correlation is more intuitive with, e.g., ``Share of Finnish speakers, %`` and ``Share of Swedish speakers, %`` having a strong negative correlation.

Relevant to migration, we see, e.g., that the ``Share of persons in urban area, %`` is negatively correlated with ``Share of persons born in area of residence, %`` suggesting increasing migration to urban areas.


```{figure} ./images/male_migri_stats_corr.png
---
height: 500px
name: males-mun-stats-corr-fig
---
Correlation of male migration and municipality statistics.
```

Inspecting  correlations of ``Migration`` shown in {numref}`Fig. {number}<males-mun-stats-migration-corr-fig>` reveals, e.g., that

* Persons of working age correate with the migration more than other age groups.
* Demographic and economic dependency ratios are negatively correlated with the migration.
* Share of people with foreign background is positively correlated with migration.
* Urban areas experience higher migration.

Correlation for departure migration is similar (see notebooks for details).
There were no large differences between males and females.



```{figure} ./images/male_migri_stats_migration_corr.png
---
height: 500px
name: males-mun-stats-migration-corr-fig
---
Correlation of male migration and municipality statistics.
```

We can also plot the correlation of departure migration by years, see {numref}`Fig. {number}<male-migri-stats-migration-corr-departure-yearly-fig>`, which shows that most features are stable, but that some municipalities apparently have experienced smaller increase of population around the years 2002-2005 and 2020-2022.


```{figure} ./images/male_migri_stats_migration_corr_departure_yearly.png
---
height: 200px
name: male-migri-stats-migration-corr-departure-yearly-fig
---
Correlation of male departure migration and municipality statistics.
```

### Distibution of selected municipality features and migration

We can further study the differences between the arrival and the departure municipalities.
Looking closer at the top six ratio-type features with the largest differences between the arrival and the departure municipalities (for males) in {numref}`Fig. {number}<diff-histograms-male-top6-fig>` we see that

* Economic dependency ratio tends to be lower in the destination municipalities (less unemployment).
* People tend to move to municipalities with less of the original population born there (urbanization).
* Urban dwelling is more popular than rural.



```{figure} ./images/diff_histograms_males_top6.png
---
height: 500px
name: diff-histograms-male-top6-fig
---
Distribution of ratio-type features between Arrival and Departure municipalities for males, aggregated for years 1990-2023. Top 6 features with the largest absolute weighted (by migration count) mean are shown.
```

Net migration per municipality (arrival - departure) is another interesting feature. 
The PCA plot {numref}`Fig. {number}<biplot-male-fig>` on municipality net migration and the mean feature values visualizes how net migration seems to be driven by working age population and the share of urban dwellers.
On the other hand, average age and economic dependency ratio points in the opposite direction of the net migration.
Another intersting observation is the similarity of the share of persons in peri-urban areas and those aged under 15; perhaps families with children favor peri-urbanicity.


```{figure} ./images/biplot_male.png
---
height: 500px
name: biplot-male-fig
---
PCA bilplot for municipality net male migration aggregated for years 1990-2023. Top 20 features and net migration are shown.
```

### Do females migrate more often and further?

One of the hypotheses set in the beginning was that females migrate more often and further.
Indeed, for the most largest municipalities excluding Espoo, {numref}`Fig. {number}<arrival-mig-by-mun-fig>`, females seem to be the more frequent arrivers than males.

```{figure} ./images/arrival_mig_by_mun.png
---
height: 300px
name: arrival-mig-by-mun-fig
---
Total arrival migration by municipality and sex for years 1990-2023.
```
Furthermore, females seem to move somewhat further distances than males, {numref}`Fig. {number}<female-dist-binned-fig>`.
It is interesting to note that both males and females move further on average in the more recent years than in the 1990s.


```{figure} ./images/female_male_distance_person_km_binned.png
---
height: 200px
name: female-dist-binned-fig
---
Migration distance weighted by migration counts, binned by years.
```

### Visualizing migration flows

We can visualize the migrations between municipalities in a map format, as in {numref}`Fig. {number}<female-map-migri-binned-fig>` (shown for females only).
The migration magnitude is normalized by the total migration count for each year bin.
It appears that there is a dozen or so largest municipalities that account for most migrations.
There does not seem to be big differences between the years, but at least for Oulu, the migration is more frequent in the recent year bins compared to the 1990-1996.


```{figure} ./images/finland_female_migration_binned_normalized.png
---
height: 600px
name: female-map-migri-binned-fig
---
Migrations of females shown, binned and normalized by years.
```

From the map it is difficult to discern the migrations between specific municipalities.
On the other hand, the chord diagrams in {numref}`Fig. {number}<diff-chords-fig>` show pairwise migrations more clearly; the figures show the difference of migration counts to the baseline years 1990-1996.
Arrow end shows the arrival municipality, and the segment width the total relative migration for the municipality.
For example, comparing the panel {numref}`Fig. {number}<diff-chords-fig>`E to {numref}`Fig. {number}<diff-chords-fig>`A-D we can see that the migration from Espoo to Helsinki has increased, but also from Helsinki to elsewhere.
Vantaa has experienced greatly increased migration.
The figure suggests that the total migration is increasing between and into the largest municipalities supporting the urbanization hypothesis.

```{figure} ./images/diff_chords_lower-res.png
---
width: 600px
name: diff-chords-fig
---
Chord diagrams of migration flow between municipalities as a difference to baseline years 1990-1996.
```


## Community Detection

From the maps and the chord diagrams we cannot easily see any possible migration groups formed by municipalities.
Indeed, the next question arising is whether the municipalities are forming migration communities and how the communities have possibly changed over the years; this is analyzed next.
The communinity detection was performed for the migration data using the same binned years as before.
The results are shown in {numref}`Fig. {number}<mun-communities-fig>`.
Quite interestingly, we see that Lahti Community has been eaten away by other communities, mostly Tampere and Jyväskylä.
The finding is interesting and could be analyzed further (out of scope).


```{figure} ./images/mun_communities.png
---
width: 600px
name: mun-communities-fig
---
The communities detected for the temporal bins spanning 1990-2023. The largest municipality is shown bolded and named in the figure legend. Municipalities not included in the community detection are in white.
```

## Modeling

We now have seen that the municipality migration seems to be driven by urbanization when analyzed through the absolute numbers of arrival and departure.
So far we haven't however answered which factors might be resposible for municipality attractiveness when compared to other municipalities and controlled by the municipality population count.

We would like to make a time series model that would incorporate the basic Statistics Finland municipality features from the earlier analyses.
The initial idea was to supplement the data with a set of selected health indices fetched from Sotkanet and housing prices, but it turned out that for many of the municipalities this data was not readily available.
The models were therefore fit only on migration and basic municipality statics as detailed below.
In the models, we consentrate on net migration scaled by the yearly population of the respective municipality.
This does not control for persons that have migrated from or to other countries, or those born or diseased; this is left for future efforts.


The {numref}`Fig. {number}<net-migri-fig>` shows normalized net migration for the 89 municipalities.
As we can see, the net migration varies a lot by years.

```{figure} ./images/net-migri.png
---
width: 600px
name: net-migri-fig
---
Net municipality migration (arrival - departure) normalized by the yearly population count of the respective municipality.
```

### TFT model

We used ``Darts`` library to fit a Temporal Fusion Transformer (TFT) model on the net migration time series.
The model was global, meaning that it took as input all municipalities (the migration and basic statistics covariates) at once.
Municipality labels were encoded as static covariates.
The model type was chosen due to its explainability and probabilistic ouput useful for sampling based confidence interval calculations.
[Alternative](https://unit8co.github.io/darts/index.html#forecasting-models) models include, e.g., N-BEATS and its variants, but they are not as expalainable as TFT.
Hyperparemeters were optimized with ``Optuna``.

As an aside, in the initial tries (not shown) we fit a TFT model on the arrival counts and found that the model consistently under-estimated the growing migration trend of the large municipalities.
This behaviour seems to be in line with TFT being a good local approximator, but struggling with longer time trends.
The solution was to do a simple linear detrending as a preprocessing step.
The detrending meant that the TFT model would not have been able to accurately predict the decreasing trends should they happen.
Alternative to linear detrending, the trend could perhaps have been calculated for a chunck of years at a time, which would have allowed the trend direction to change.


As we however then decided to concentrate on *net migration* normalized by the population of the municiaplity, no de-trending was needed, {numref}`Fig. {number}<net-migri-fig>`.


The input to the model was comprised of the ratio-type features (apart from the log-transformed land area) which were controlled for correlation, and normalized to zero mean and unit variance.
There was no missing data.
The training set comprised the years 1990-2014, and validation the years 2015-2023.


| Variable                                    |
|---------------------------------------------|
| Average age, both sexes_arr                  |
| Demographic dependency ratio_arr            |
| Economic dependency ratio_arr                |
| Land area, km²_arr                           |
| Population density_arr                       |
| Share of Finnish speakers, %_arr             |
| Share of foreign citizens, %_arr              |
| Share of persons aged under 15, %_arr         |
| Share of persons belonging to other religious groups, %_arr |
| Share of persons belonging to the Evangelical Lutheran Church, %_arr |
| Share of persons born in the area of residence, %_arr        |
| Share of persons in inner urban area, %_arr                   |
| Share of persons in local centres in rural areas, %_arr       |
| Share of persons in outer urban area, %_arr                   |
| Share of persons in peri-urban area, %_arr                    |
| Share of persons in rural areas close to urban areas, %_arr   |
| Share of persons in rural areas, %_arr                         |
| Share of persons in rural heartland areas, %_arr              |
| Share of persons in sparsely populated rural areas, %_arr     |
| Share of persons living in the area of birth, %_arr           |
| year                                                           |
| net_migration                                                  |
| municipality                                                  |



#### TFT results

TFT turned out to be powerful and easy to overfit to historical data.
We first performed extensive hyperparameter tuning with Optuna.
Then a large model was fit, with train and validation loss (mean MAPE) plotted.
Based on the validation loss, we fit a smaller model to avoid overfitting.
The predictive performance was not great, with many measured net migrations in the validation set being outside the predicted 95% confidence interval; perhaps the used features were not enough to explain the net migration.

There was no strict test set, instead we tried to explain which features are important (encoder importance, calculated with ``Darts TFTExpalainer``) for predicting the validation set.
Although this means there was information leakage from the validation to the training set during the hyperparameter optimization, this is not a big problem here since we could as well have tried to explain the model's behaviour on the training set.


Unfortunately, the purported explainability was not achieved:
We spent a considerable amount of time on trying to fit the TFT model such that the variable importance interpretation would be robust.
However, even seemingly small changes in the model training protocol or data input lead to different conclusions about the variable importance.


Nonentheless, below we show the variable importance calculated on the validation set, {numref}`Fig. {number}<enc-importance-hclust-fig>`.
We can try to say that
1. Past net migration itself is important for explaining the future net migration.
2. Population density seems to be independently important from the other features (apart from the net migration).
3. There is a group of less important features including land area and the demographic dependency.
4. The rest of the features are grouped together.
5. Municipalities tend to be grouped in large clusters, but there are some smaller groups standing out, namely Espoo--Forssa, and Alavus--Eura--Hamina--Heinola.

**However, these intrepretations are not reliable due to the TFT model fitting difficulties!**



```{figure} ./images/enc-importance-hclust.png
---
width: 600px
name: enc-importance-hclust-fig
---
Variable importance in the TFT model for validation set, with features and municipalities clustered. Importance log-transformed for larger visual contrast.
```

### LightGBM model

To address the uncertainty with the TFT model, the same input was used to fit a LightGBM model.
The input was as with the TFT model, but in tabular form, and was randomly split to train, validation and test set (3:1:1).
Hyperparameters were optimized with Optuna and the model output (RMSE relative to min-to-max range on the test set was 7.49%) explained with SHAP,  {numref}`Fig. {number}<lgb-shap-train-fig>`.
Although the model is simple, there are interesting observations to be made, but should be taken with caution.
1. Higher economic dependecy ratio is associated with lower migration propensity.
2. Higher share of persons in rural areas close to urban areas are somewhat surprisingly associated with higher net migration.
3. Higher share of children aged under 15 increase net migration.
4. Lower average age is associated with a higher net migration.
5. The most attractive municipalities are quite small in population.


```{figure} ./images/lgb-shap-train.png
---
width: 600px
name: lgb-shap-train-fig
---
SHAP-values for the training set of the LightGBM model for the six most important variables. Ten municipalities with the largest net migration summed for years 1990-2023 shown in color.
```


## Conclusions

All in all, valuable information on municipality migration in Finland was discovered through the analyses and models.
Reflecting at the intial hypothesis, we found evidence that:

* In absolute migration counts, people tend to move to and from the bigger municipalities (urbanization).
* Females move more frequently and further.
* When normalized by municipality population, the largest municipalities do not experience the most net migration on average.
* There are migration municipality communities formed, and the communities have changed over the years.
* Modeling normalized net migration time series with TFT is difficult with the data available here.
* Good economic situation and young or working-age population increase the net migration.

There are many ways the project could be made better or extended.
The future efforts could include:

* Including migration from and to other countries.
* Accounting for births and deaths.
* Statistical hypothesis testing.
* More careful time series modeling (e.g., analyzing autocorrelation).
* Clustering of the time series with, e.g., [DTW](https://tslearn.readthedocs.io/en/stable/user_guide/dtw.html#dtw).
* Time series featurization for LightGBM model with, e.g., [tsfresh](https://tsfresh.readthedocs.io/en/latest/).
* Adding migration distance to the models (many probably tend to move close).
* Including Sotkanet data by looking for more complete variables or averaging over the larger areas.
* Consulting demographics experts.



