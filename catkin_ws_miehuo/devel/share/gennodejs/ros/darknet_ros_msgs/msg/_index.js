
"use strict";

let BoundingBoxes = require('./BoundingBoxes.js');
let ObjectCount = require('./ObjectCount.js');
let BoundingBox = require('./BoundingBox.js');
let CheckForObjectsActionGoal = require('./CheckForObjectsActionGoal.js');
let CheckForObjectsActionResult = require('./CheckForObjectsActionResult.js');
let CheckForObjectsActionFeedback = require('./CheckForObjectsActionFeedback.js');
let CheckForObjectsFeedback = require('./CheckForObjectsFeedback.js');
let CheckForObjectsGoal = require('./CheckForObjectsGoal.js');
let CheckForObjectsAction = require('./CheckForObjectsAction.js');
let CheckForObjectsResult = require('./CheckForObjectsResult.js');

module.exports = {
  BoundingBoxes: BoundingBoxes,
  ObjectCount: ObjectCount,
  BoundingBox: BoundingBox,
  CheckForObjectsActionGoal: CheckForObjectsActionGoal,
  CheckForObjectsActionResult: CheckForObjectsActionResult,
  CheckForObjectsActionFeedback: CheckForObjectsActionFeedback,
  CheckForObjectsFeedback: CheckForObjectsFeedback,
  CheckForObjectsGoal: CheckForObjectsGoal,
  CheckForObjectsAction: CheckForObjectsAction,
  CheckForObjectsResult: CheckForObjectsResult,
};
