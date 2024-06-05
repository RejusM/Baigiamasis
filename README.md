# Bėgimo Varžybų Valdymo Sistema

 Programa, skirta trail bėgimo varžybų valdymui. Ji leidžia vartotojams registruotis į varžybas, peržiūrėti dalyvių statistiką ir matyti varžybų rezultatus. Administratoriai gali valdyti varžybas, dalyvius ir rezultatus per administratoriaus sąsają.

## Funkcionalumas

- **Vartotojo registracija**: Vartotojai gali registruotis ir kurti profilius.
- **Varžybų valdymas**: Kurkite, peržiūrėkite ir valdykite trail bėgimo varžybas.
- **Dalyvių registracija**: Vartotojai gali registruotis į konkrečias varžybas ir trasas.
- **Rezultatų valdymas**: Administratoriai gali pridėti ir peržiūrėti varžybų rezultatus.
- **Statistika**: Peržiūrėkite dalyvių statistiką, įskaitant suskirstymą pagal komandas ir lytį.
- **Administratoriaus sąsaja**: Vartotojų, varžybų ir registracijų valdymas.

### Vartotojo funkcijos

- **Registracija ir prisijungimas**: Sukurkite paskyrą ir prisijunkite, kad galėtumėte naudotis daugiau funkcijų.
- **Varžybų peržiūra**: Peržiūrėkite visų būsimos ir praėjusios varžybų sąrašą.
- **Registracija į varžybas**: Užsiregistruokite į galimas varžybas ir trasas.
- **Rezultatų peržiūra**: Peržiūrėkite savo dalyvavimo rezultatus.
- **Statistikos peržiūra**: Patikrinkite dalyvių statistiką pagal skirtingas varžybas.

### Administratoriaus funkcijos

- **Vartotojų valdymas**: Peržiūrėkite ir valdykite registruotus vartotojus.
- **Varžybų kūrimas ir valdymas**: Pridėkite naujas varžybas, atnaujinkite varžybų informaciją ir ištrinkite varžybas.
- **Registracijų valdymas**: Patvirtinkite arba atmeskite dalyvių registracijas.
- **Rezultatų valdymas**: Pridėkite ir atnaujinkite varžybų rezultatus.

### Modeliai

- **UserProfile**: Papildo numatytąjį vartotojo modelį papildoma informacija.
- **Team**: Atstovauja komandą, prie kurios gali prisijungti dalyviai.
- **Track**: Atstovauja skirtingas varžybų trasas.
- **Stage**: Atstovauja varžybų etapą.
- **RaceResult**: Saugo varžybų rezultatus.
- **OverallTeamScore**: Kaupia komandų rezultatus visose varžybose.
- **OverallUserScore**: Kaupia vartotojų rezultatus visose varžybose.
- **RaceRegistration**: Tvarko vartotojų registracijas į varžybas.

### Formos

- **UserUpdateForm**: Forma vartotojo informacijos atnaujinimui.
- **ProfileUpdateForm**: Forma vartotojo profilio informacijos atnaujinimui.
- **TrackForm**: Forma trasų pasirinkimui registracijos metu.
- **StageForm**: Forma etapų pasirinkimui filtravimo metu.

### Vaizdai (Views)

- **home**: Rodo pradinį puslapį su būsimomis ir praėjusiomis varžybomis.
- **all_stages**: Rodo visų etapų sąrašą.
- **stage_detail**: Rodo detalę informaciją apie konkretų etapą.
- **register_user**: Tvarko vartotojų registraciją.
- **profile**: Rodo vartotojo profilio puslapį.
- **edit_profile**: Tvarko profilio redagavimą.
- **review_registrations**: Leidžia administratoriui peržiūrėti ir tvarkyti registracijas.
- **register_for_race**: Tvarko registraciją į varžybas.
- **participants_list**: Rodo dalyvių sąrašą pagal etapą.
- **race_result_list**: Rodo varžybų rezultatus.
- **personal_results**: Rodo prisijungusio vartotojo asmeninius rezultatus.
- **team_results**: Rodo vartotojo komandos rezultatus.
- **overall_user_scores**: Rodo bendrus vartotojų rezultatus.
- **overall_team_scores**: Rodo bendrus komandų rezultatus.
- **participants_statistics**: Rodo dalyvių statistiką.
- **filtered_results**: Rodo filtruotus rezultatus.

### Šablonai

- **base.html**: Pagrindinis šablonas su bendru išdėstymu.
- **home.html**: Pradinio puslapio šablonas.
- **all_stages.html**: Šablonas visų etapų peržiūrai.
- **stage_detail.html**: Šablonas etapo detalės peržiūrai.
- **registration.html**: Vartotojo registracijos šablonas.
- **profile.html**: Vartotojo profilio šablonas.
- **edit_profile.html**: Profilių redagavimo šablonas.
- **review_registrations.html**: Registracijų peržiūros šablonas.
- **register_for_race.html**: Varžybų registracijos šablonas.
- **participants_list.html**: Dalyvių sąrašo šablonas.
- **race_result_list.html**: Varžybų rezultatų šablonas.
- **personal_results.html**: Asmeninių rezultatų šablonas.
- **team_results.html**: Komandos rezultatų šablonas.
- **overall_user_scores.html**: Bendrų vartotojų rezultatų šablonas.
- **overall_team_scores.html**: Bendrų komandų rezultatų šablonas.
- **participants_statistics.html**: Dalyvių statistikos šablonas.
- **filtered_results.html**: Filtruotų rezultatų šablonas.
