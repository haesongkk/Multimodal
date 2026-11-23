def category(name):
 s=name.lower()
 if s=='sm_kitchen':return 'Rug','rugRectangle'
 for keys,cat,ken in [
  (['leathercouch'],'Armchair','loungeChairRelax'),
  (['vintage_chair'],'Chair','chairCushion'),
  (['bookshelf'],'Bookshelf','bookcaseOpen'),
  (['desk'],'Desk','desk'),
  (['fridge_magnet'],'Paper',None),
  (['fridge'],'Fridge','kitchenFridge'),
  (['stove'],'Stove','kitchenStove'),
  (['countertop_c'],'Table','kitchenCabinet'),
  (['countertop_b'],'Cabinet','kitchenSink'),
  (['countertop'],'Cabinet','kitchenCabinetDrawer'),
  (['kitchen_shelf_a'],'UpperCabinet','kitchenCabinetUpperDouble'),
  (['kitchen_shelf'],'Table','shelf'),
  (['bathtub'],'Bathtub','bathtub'),
  (['toilet'],'Toilet','toilet'),
  (['bathroom_sink'],'Sink','bathroomSinkSquare'),
  (['btwindow'],'Frame','bathroomMirror'),
  (['vintage_dining_table'],'Table','tableRound'),
  (['tablebasse','smalltable','tablemin'],'Table','tableCoffee'),
  (['tvset'],'Television','televisionVintage'),
  (['microwave'],'Microwave','kitchenMicrowave'),
  (['toaster'],'Microwave','toaster'),
  (['blender'],'Bottle','kitchenBlender'),
  (['radio'],'Radio','radio'),
  (['clock','timer'],'Clock',None),
  (['window'],'Window','wallWindow'),
  (['door_frame','curtain_rod','pot_holder','towel_rack'],'Utensil',None),
  (['door'],'Door','doorway'),
  (['frames'],'Frame',None),
  (['book'],'Book',None),
  (['flowersplant'],'Plant','plantSmall1'),
  (['flowerpot'],'Pot','plantSmall2'),
  (['bottles','ceramic_bottle','glass_jar','spoon_jar'],'Bottle',None),
  (['mug','glass_cup','water_glass'],'Mug',None),
  (['bowl','foodpot'],'Bowl',None),
  (['plate'],'Plate',None),
  (['pot0','saucepan'],'Pan',None),
  (['carpet','placemat'],'Rug','rugRectangle'),
  (['chandelier','light_bulb'],'Lamp','lampSquareCeiling'),
  (['trash'],'Trash','trashcan'),
  (['letter','drawing','sticky','napkin'],'Paper',None),
  (['curtain','towel','glove'],'Cloth',None),
  (['candle'],'Candle',None),
  (['food_sm','bread','pepper'],'Fruit',None),
  (['knife','spoon','fork','ladel','ustensil','broom','shower_head','crayon'],'Utensil',None),
  (['foodcan','cereal','cookie','scotch','soap','sponge'],'Box',None),
 ]:
  if any(k in s for k in keys):return cat,ken
 return 'Box',None

# Authored meshes face -Y; existing asset front axes vary.
def source_turn(name,cat):
 if cat=='Armchair':return -90
 if cat in ['Bookshelf','Desk','Fridge','Stove','Cabinet','UpperCabinet','Television','Radio','Microwave','Frame','Clock','Window']:return 180
 return 0
