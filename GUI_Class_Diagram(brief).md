## 1.GUI
___

```mermaid
classDiagram
  direction LR

   MainWindowTk *-- PageTab
   PageTab *-- PageFrame
   PageTab *-- NewFrame
  PageFrame *-- WindowCanvas
   WindowCanvas *-- WorldGrid__

   MainWindowTk *-- Tooltab
  Tooltab *-- HomeFrame__

```
## 2. World Grid Class Diagram
___

```mermaid
classDiagram
  WorldGrid *-- GridShapes
  GridShapes *-- Background
  GridShapes *-- Cable
  GridShapes *-- Coupler
  GridShapes *-- ActiveEquipment
```
## 3. HomeFrame Class Diagram
___
```mermaid
classDiagram
  HomeFrame *-- AddCable
  HomeFrame *-- AddCoupler
  HomeFrame *-- AddRiser
  HomeFrame *-- AddAmplifier

  class 
```

