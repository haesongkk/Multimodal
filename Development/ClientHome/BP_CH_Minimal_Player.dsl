(event EventBeginPlay
(bind position (Transformation|GetActorLocation))
(bind destination (Math|Vector|MakeVector :X (select (< (- (.x position) 850.0) -1230.0) -1230.0 (select (> (- (.x position) 850.0) 30.0) 30.0 (- (.x position) 850.0))) :Y (select (< (.x position) -230.0) (select (< (.y position) -180.0) -180.0 (select (> (.y position) 350.0) 350.0 (.y position))) (select (< (.y position) -350.0) -350.0 (select (> (.y position) 350.0) 350.0 (.y position)))) :Z 480.0))
(Transformation|SetWorldLocation :self (Variables|디폴트|GetViewCamera) :NewLocation destination))
(event EventTick (DeltaSeconds)
(bind position (Transformation|GetActorLocation))
(bind destination (Math|Vector|MakeVector :X (select (< (- (.x position) 850.0) -1230.0) -1230.0 (select (> (- (.x position) 850.0) 30.0) 30.0 (- (.x position) 850.0))) :Y (select (< (.x position) -230.0) (select (< (.y position) -180.0) -180.0 (select (> (.y position) 350.0) 350.0 (.y position))) (select (< (.y position) -350.0) -350.0 (select (> (.y position) 350.0) 350.0 (.y position)))) :Z 480.0))
(Transformation|SetWorldLocation :self (Variables|디폴트|GetViewCamera) :NewLocation (Math|Interpolation|VInterpTo :Current (Transformation|GetWorldLocation :self (Variables|디폴트|GetViewCamera)) :Target destination :DeltaTime DeltaSeconds :InterpSpeed 3.5)))
