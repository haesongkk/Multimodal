(event EventBeginPlay
(bind position (Transformation|GetActorLocation))
(bind destination (Math|Vector|MakeVector :X (select (< (.x position) -650.0) -650.0 (select (> (.x position) 750.0) 750.0 (.x position))) :Y (- (select (< (.y position) -350.0) -350.0 (select (> (.y position) 430.0) 430.0 (.y position))) 1000.0) :Z 720.0))
(Transformation|SetWorldLocation :self (Variables|Default|GetViewCamera) :NewLocation destination))
(event EventTick (DeltaSeconds)
(bind position (Transformation|GetActorLocation))
(bind destination (Math|Vector|MakeVector :X (select (< (.x position) -650.0) -650.0 (select (> (.x position) 750.0) 750.0 (.x position))) :Y (- (select (< (.y position) -350.0) -350.0 (select (> (.y position) 430.0) 430.0 (.y position))) 1000.0) :Z 720.0))
(Transformation|SetWorldLocation :self (Variables|Default|GetViewCamera) :NewLocation (Math|Interpolation|VInterpTo :Current (Transformation|GetWorldLocation :self (Variables|Default|GetViewCamera)) :Target destination :DeltaTime DeltaSeconds :InterpSpeed 3.5)))
