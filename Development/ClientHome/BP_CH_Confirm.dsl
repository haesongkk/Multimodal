(fn Confirm () (if (and (Variables|Default|GetPopup) (not (Variables|Default|GetComplete))) (Variables|Default|SetPopup false) (if (and (== (Variables|Default|GetCount) 3) (not (Variables|Default|GetDeduced))) (Variables|Default|SetDeduced true) (Variables|Default|SetTitle "추리 완료")
(Variables|Default|SetMessage "코코는 창문으로 나간 것 같다. 현관문을 열고 밖으로 나가자.")
(Variables|Default|SetPopup true))))