DLR-PT-Bewerbungsformular
=========================

Projekttitel
------------

Flohmarkt (arbeitstitel)

Beschreibe dein Projekt kurz
----------------------------

Flohmarkt möchte eine dezentrale Plattform für Kleinanzeigen werden. Dazu wollen wir eine
selbst hostbare Webanwendung schreiben, die einerseits ihren Nutzern und Nutzerinnen ein
aehnliches Erlebnis bietet, wie andere etablierte Inseratplattformen, auf der anderen seite
aber auch in der Lage ist, Inserate mit anderen Instanzen derselben Software auszutauschen.

Welchem Themenfeld ordnest du dein Projekt zu?
----------------------------------------------

Civic Tech

Welche gesellschaftlichen Herausforderungen willst du mit deinem Projekt angehen
--------------------------------------------------------------------------------

Wir sehen drei Kernpunkte, in denen Flohmarkt hilft, die Welt zu verbessern:
1. Einerseits fördert es den Re-Use-Gedanken, nach dem ein in zweiter Hand genutzter Gegenstand
immer besser ist als ein entsorgter Gegenstand. Weiternutzung spart Ressourcen und senkt die
Notwendigkeit der Nachproduktion.
2. Wir möchten die Nutzerschaft der Plattform in Kommuniques (z.B. auf der Projektseite) dazu
motivieren, Ihren Flohmarkt-Instanzen einen geographischen Bezug, zum Beispiel einer Stadt zu
geben. So sollen sich lokale Communities bilden, die Gegenstände untereinander austauschen.
Dadurch ergeben sich kürzere Transportwege und somit eingesparter CO2-Ausstoss. Ferner hoffen
wir, dass örtlich gebundene Instanzen vermehrt mit Instanzen föderieren, die sich in ihrer
unmittelbaren geographischen Umgebung befinden und so, organisch, ein Netz der kürzesten Wege
entsteht.
3. Wir halten Monopole für schädlich für die Gesamtgesellschaft, da sie Innovation ausbremsen
und Selbstbestimmung der Nutzer und Nutzerinnen untergraben. Deswegen wollen wir eine 
nutzenswerte Alternative zum gegenwärtigen Marktführer aufbauen.

Wie willst du dein Projekt technisch umsetzen?
----------------------------------------------

Wir beabsichtigen, ein Backend in den Programmiersprache Go zu entwickeln. Go ist derzeit recht
so hoffen wir, eine stabile Community an mitentwicklern zu bekommen. Zur Föderation Nutzen wir
das bereits erfolgreich erprobte W3C-Protokol ActivityPub, welches auch von z.B. Mastodon und
Peertube eingesetzt wird. Wir beabsichtigen, auch mit anderen Fediverse- [ActivityPub-nutzenden]
Softwares kompatibel zu werden, sodass man bspw. als reiner Mastodon-Nutzer einen Artikel
auf Flohmarkt kaufen kann. Datenbankseitig werden wir auf eine Collection-Dokumentenbasierte
NoSQL-Datenbank setzen.
Frontendseitig soll ein Shopsoftware-artiges Interface auf basis von VueJS entstehen.

Hast du schon an der Idee gearbeitet?
-------------------------------------

Abseits von Überlegungen zum Techstack und der Featurebreite für ein Minimum Viable Product
wurde noch nicht an dem Projekt gearbeitet.

Link zum bestehenden Projekt
-----------------------------

- 

Welche ähnlichen Ansätze gibt es bereits?
-----------------------------------------

Laut der Liste der Aktuell bestehenden ActivityPub-Softwares auf der Wikipedia existiert
derzeit keine Software für Kleinanzeigen.
Es existieren regionale Kleinanzeigenplattformen, allerdings werden diese kommerziell
betrieben und implementieren kein Föderationsprotokoll, sind also nicht dezentral.

Wer ist die Zielgruppe und wie soll dein Projekt sie erreichen?
---------------------------------------------------------------

Die Zielgruppe für das Projekt sind alle Menschen, die Gegenstände aus zweiter Hand erwerben
oder anbieten wollen.
Wir beabsichtigen auf Konferenzen über die Existenz des Projektes zu sprechen. Wir erhoffen
uns, dass durch den geographischen Bezug der einzelnen Instanzen einfacher Mund-zu-Mund-
Propaganda stattfindet, als bei einem reinen Internetbezogenen Projekt.

An welchen Software-Projekten hast du / habt Ihr bereits gearbeitet?
--------------------------------------------------------------------

## Freie Software

  * OParl - Referenz-Clientimplementierung der offenen Schnittstelle für Ratsinformationssysteme (OParl)[https://github.com/OParl/liboparl]
  * libgtkflow - Eine Flowgraph-Library für Gtk+3 zur Darstellung und Editierung von Prozessen. [https://notabug.org/grindhold/libgtkflow]
  * libhttpseverywhere - HTTPSEverywhere für Desktop-Applikationen [https://gitlab.gnome.org/GNOME/libhttpseverywhere]
  * linseneintops - CAM-Software für die Herstefllung von planokonvexen Linsen aus Acryl [https://codeberg.org/grindhold/linseneintopf]
  * u.v.m. → https://notabug.org/grindhold und https://codeberg.org/grindhold

## Kommerzielle Projekte

  * DEMOSPlan, Websoftware für interaktive Bürgerbeteiligung in der Bauleitplanung - Bei DEMOS E-Partizipation GmbH
  * Demos Planning Pipeline, One-Stop-Lösung für die Abarbeitung und Verteilung von AI-Rechenjobs - Bei DEMOS E-Parizipation GmbH

Erfahrung, Hintergrund, Motivation, Perspektive: Was sollten wir über dich wissen?
----------------------------------------------------------------------------------

Bewerbt ihr Euch als Team um die Förderung?
-------------------------------------------

Nein.

Namen der Teammitglieder
------------------------

 -

Wie viele Stunden willst du (bzw will das Team) in den 6 Monaten Förderzeitraum insgesamt an der Umsetzung arbeiten?
--------------------------------------------------------------------------------------------------------------------

Skizziere kurz die wichtigsten Meilensteiene, die im Förderzeitraum umgesetzt werden sollen
-------------------------------------------------------------------------------------------

  * Wir schreiben ein IAM-System um die Rollen User, Admin und Moderation abbilden zu können.
  * Wir schreiben einen CRUD-Cyclus für das Zentrale Objekt im System, das Inserat
  * Wir schaffen eine Möglichkeit, im Bezug auf Inserate, Nachrichten und Kaufinteressensbekundungen
    austauschen zu können
  * Wir stellen Interoperabilität mit anderen Flohmarkt-Instanzen her
  * Wir stellen Interoperabilität mit anderen ActivityPub-Basierten softwares her, mindestens
  * jedoch Mastodon.

Checkliste
----------



