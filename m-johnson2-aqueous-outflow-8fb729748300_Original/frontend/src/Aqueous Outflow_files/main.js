(window["webpackJsonp"] = window["webpackJsonp"] || []).push([["main"],{

/***/ "./node_modules/webpack/hot sync ^\\.\\/log$":
/*!*************************************************!*\
  !*** (webpack)/hot sync nonrecursive ^\.\/log$ ***!
  \*************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

var map = {
	"./log": "./node_modules/webpack/hot/log.js"
};


function webpackContext(req) {
	var id = webpackContextResolve(req);
	var module = __webpack_require__(id);
	return module;
}
function webpackContextResolve(req) {
	var id = map[req];
	if(!(id + 1)) { // check for number or string
		var e = new Error("Cannot find module '" + req + "'");
		e.code = 'MODULE_NOT_FOUND';
		throw e;
	}
	return id;
}
webpackContext.keys = function webpackContextKeys() {
	return Object.keys(map);
};
webpackContext.resolve = webpackContextResolve;
module.exports = webpackContext;
webpackContext.id = "./node_modules/webpack/hot sync ^\\.\\/log$";

/***/ }),

/***/ "./src/$$_lazy_route_resource lazy recursive":
/*!**********************************************************!*\
  !*** ./src/$$_lazy_route_resource lazy namespace object ***!
  \**********************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

function webpackEmptyAsyncContext(req) {
	// Here Promise.resolve().then() is used instead of new Promise() to prevent
	// uncaught exception popping up in devtools
	return Promise.resolve().then(function() {
		var e = new Error("Cannot find module '" + req + "'");
		e.code = 'MODULE_NOT_FOUND';
		throw e;
	});
}
webpackEmptyAsyncContext.keys = function() { return []; };
webpackEmptyAsyncContext.resolve = webpackEmptyAsyncContext;
module.exports = webpackEmptyAsyncContext;
webpackEmptyAsyncContext.id = "./src/$$_lazy_route_resource lazy recursive";

/***/ }),

/***/ "./src/app/app-routing.module.ts":
/*!***************************************!*\
  !*** ./src/app/app-routing.module.ts ***!
  \***************************************/
/*! exports provided: AppRoutingModule */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "AppRoutingModule", function() { return AppRoutingModule; });
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm5/core.js");
/* harmony import */ var _angular_router__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/router */ "./node_modules/@angular/router/fesm5/router.js");
/* harmony import */ var _simulation_simulation_component__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./simulation/simulation.component */ "./src/app/simulation/simulation.component.ts");
/* harmony import */ var _visual_editor_visual_editor_component__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./visual-editor/visual-editor.component */ "./src/app/visual-editor/visual-editor.component.ts");
var __decorate = (undefined && undefined.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};




var routes = [
    { path: 'conditions', component: _simulation_simulation_component__WEBPACK_IMPORTED_MODULE_2__["SimulationComponent"] },
    { path: 'visual-editor', component: _visual_editor_visual_editor_component__WEBPACK_IMPORTED_MODULE_3__["VisualEditorComponent"] }
];
var AppRoutingModule = /** @class */ (function () {
    function AppRoutingModule() {
    }
    AppRoutingModule = __decorate([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_0__["NgModule"])({
            imports: [_angular_router__WEBPACK_IMPORTED_MODULE_1__["RouterModule"].forRoot(routes)],
            exports: [_angular_router__WEBPACK_IMPORTED_MODULE_1__["RouterModule"]]
        })
    ], AppRoutingModule);
    return AppRoutingModule;
}());



/***/ }),

/***/ "./src/app/app.component.css":
/*!***********************************!*\
  !*** ./src/app/app.component.css ***!
  \***********************************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = ""

/***/ }),

/***/ "./src/app/app.component.html":
/*!************************************!*\
  !*** ./src/app/app.component.html ***!
  \************************************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = "<!--The content below is only a placeholder and can be replaced.-->\n<app-sidenav></app-sidenav>\n"

/***/ }),

/***/ "./src/app/app.component.ts":
/*!**********************************!*\
  !*** ./src/app/app.component.ts ***!
  \**********************************/
/*! exports provided: AppComponent */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "AppComponent", function() { return AppComponent; });
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm5/core.js");
var __decorate = (undefined && undefined.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};

var AppComponent = /** @class */ (function () {
    function AppComponent() {
        this.title = 'Aqueous Outflow Model';
    }
    AppComponent = __decorate([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_0__["Component"])({
            selector: 'app-root',
            template: __webpack_require__(/*! ./app.component.html */ "./src/app/app.component.html"),
            styles: [__webpack_require__(/*! ./app.component.css */ "./src/app/app.component.css")]
        })
    ], AppComponent);
    return AppComponent;
}());



/***/ }),

/***/ "./src/app/app.module.ts":
/*!*******************************!*\
  !*** ./src/app/app.module.ts ***!
  \*******************************/
/*! exports provided: AppModule */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "AppModule", function() { return AppModule; });
/* harmony import */ var _angular_platform_browser__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @angular/platform-browser */ "./node_modules/@angular/platform-browser/fesm5/platform-browser.js");
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm5/core.js");
/* harmony import */ var _angular_common_http__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @angular/common/http */ "./node_modules/@angular/common/fesm5/http.js");
/* harmony import */ var _app_component__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./app.component */ "./src/app/app.component.ts");
/* harmony import */ var _angular_platform_browser_animations__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @angular/platform-browser/animations */ "./node_modules/@angular/platform-browser/fesm5/animations.js");
/* harmony import */ var _angular_flex_layout__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @angular/flex-layout */ "./node_modules/@angular/flex-layout/esm5/flex-layout.es5.js");
/* harmony import */ var _angular_cdk_layout__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @angular/cdk/layout */ "./node_modules/@angular/cdk/esm5/layout.es5.js");
/* harmony import */ var _angular_material__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! @angular/material */ "./node_modules/@angular/material/esm5/material.es5.js");
/* harmony import */ var _simulation_simulation_component__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ./simulation/simulation.component */ "./src/app/simulation/simulation.component.ts");
/* harmony import */ var _angular_forms__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! @angular/forms */ "./node_modules/@angular/forms/fesm5/forms.js");
/* harmony import */ var _edit_constants_dialog_edit_constants_dialog_component__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! ./edit-constants-dialog/edit-constants-dialog.component */ "./src/app/edit-constants-dialog/edit-constants-dialog.component.ts");
/* harmony import */ var _app_routing_module__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! ./app-routing.module */ "./src/app/app-routing.module.ts");
/* harmony import */ var _sidenav_sidenav_component__WEBPACK_IMPORTED_MODULE_12__ = __webpack_require__(/*! ./sidenav/sidenav.component */ "./src/app/sidenav/sidenav.component.ts");
/* harmony import */ var _create_cc_dist_dialog_create_cc_dist_dialog_component__WEBPACK_IMPORTED_MODULE_13__ = __webpack_require__(/*! ./create-cc-dist-dialog/create-cc-dist-dialog.component */ "./src/app/create-cc-dist-dialog/create-cc-dist-dialog.component.ts");
/* harmony import */ var _create_stent_dialog_create_stent_dialog_component__WEBPACK_IMPORTED_MODULE_14__ = __webpack_require__(/*! ./create-stent-dialog/create-stent-dialog.component */ "./src/app/create-stent-dialog/create-stent-dialog.component.ts");
/* harmony import */ var _visual_editor_visual_editor_component__WEBPACK_IMPORTED_MODULE_15__ = __webpack_require__(/*! ./visual-editor/visual-editor.component */ "./src/app/visual-editor/visual-editor.component.ts");
/* harmony import */ var _surgery_arc_surgery_arc_component__WEBPACK_IMPORTED_MODULE_16__ = __webpack_require__(/*! ./surgery-arc/surgery-arc.component */ "./src/app/surgery-arc/surgery-arc.component.ts");
var __decorate = (undefined && undefined.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};

















var AppModule = /** @class */ (function () {
    function AppModule() {
    }
    AppModule = __decorate([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_1__["NgModule"])({
            declarations: [
                _app_component__WEBPACK_IMPORTED_MODULE_3__["AppComponent"],
                _simulation_simulation_component__WEBPACK_IMPORTED_MODULE_8__["SimulationComponent"],
                _edit_constants_dialog_edit_constants_dialog_component__WEBPACK_IMPORTED_MODULE_10__["EditConstantsDialogComponent"],
                _sidenav_sidenav_component__WEBPACK_IMPORTED_MODULE_12__["SidenavComponent"],
                _create_cc_dist_dialog_create_cc_dist_dialog_component__WEBPACK_IMPORTED_MODULE_13__["CreateCcDistDialogComponent"],
                _create_stent_dialog_create_stent_dialog_component__WEBPACK_IMPORTED_MODULE_14__["CreateStentDialogComponent"],
                _visual_editor_visual_editor_component__WEBPACK_IMPORTED_MODULE_15__["VisualEditorComponent"],
                _surgery_arc_surgery_arc_component__WEBPACK_IMPORTED_MODULE_16__["SurgeryArcComponent"]
            ],
            entryComponents: [
                _edit_constants_dialog_edit_constants_dialog_component__WEBPACK_IMPORTED_MODULE_10__["EditConstantsDialogComponent"],
                _create_cc_dist_dialog_create_cc_dist_dialog_component__WEBPACK_IMPORTED_MODULE_13__["CreateCcDistDialogComponent"],
                _create_stent_dialog_create_stent_dialog_component__WEBPACK_IMPORTED_MODULE_14__["CreateStentDialogComponent"]
            ],
            imports: [
                _angular_platform_browser__WEBPACK_IMPORTED_MODULE_0__["BrowserModule"],
                _angular_common_http__WEBPACK_IMPORTED_MODULE_2__["HttpClientModule"],
                _angular_platform_browser_animations__WEBPACK_IMPORTED_MODULE_4__["BrowserAnimationsModule"],
                _angular_cdk_layout__WEBPACK_IMPORTED_MODULE_6__["LayoutModule"],
                _angular_material__WEBPACK_IMPORTED_MODULE_7__["MatFormFieldModule"],
                _angular_material__WEBPACK_IMPORTED_MODULE_7__["MatSelectModule"],
                _angular_material__WEBPACK_IMPORTED_MODULE_7__["MatCardModule"],
                _angular_material__WEBPACK_IMPORTED_MODULE_7__["MatOptionModule"],
                _angular_material__WEBPACK_IMPORTED_MODULE_7__["MatInputModule"],
                _angular_material__WEBPACK_IMPORTED_MODULE_7__["MatDividerModule"],
                _angular_material__WEBPACK_IMPORTED_MODULE_7__["MatListModule"],
                _angular_material__WEBPACK_IMPORTED_MODULE_7__["MatCheckboxModule"],
                _angular_forms__WEBPACK_IMPORTED_MODULE_9__["FormsModule"],
                _angular_material__WEBPACK_IMPORTED_MODULE_7__["MatTooltipModule"],
                _angular_material__WEBPACK_IMPORTED_MODULE_7__["MatButtonModule"],
                _angular_material__WEBPACK_IMPORTED_MODULE_7__["MatIconModule"],
                _angular_material__WEBPACK_IMPORTED_MODULE_7__["MatDialogModule"],
                _app_routing_module__WEBPACK_IMPORTED_MODULE_11__["AppRoutingModule"],
                _angular_material__WEBPACK_IMPORTED_MODULE_7__["MatToolbarModule"],
                _angular_material__WEBPACK_IMPORTED_MODULE_7__["MatSidenavModule"],
                _angular_flex_layout__WEBPACK_IMPORTED_MODULE_5__["FlexLayoutModule"]
            ],
            providers: [],
            bootstrap: [_app_component__WEBPACK_IMPORTED_MODULE_3__["AppComponent"]]
        })
    ], AppModule);
    return AppModule;
}());



/***/ }),

/***/ "./src/app/create-cc-dist-dialog/create-cc-dist-dialog.component.css":
/*!***************************************************************************!*\
  !*** ./src/app/create-cc-dist-dialog/create-cc-dist-dialog.component.css ***!
  \***************************************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = ".start-end-container {\n  justify-content: space-between;\n  vertical-align: center;\n}\n\n.input-inline {\n  width: 20%;\n  text-align: right;\n  vertical-align: middle;\n\n}\n"

/***/ }),

/***/ "./src/app/create-cc-dist-dialog/create-cc-dist-dialog.component.html":
/*!****************************************************************************!*\
  !*** ./src/app/create-cc-dist-dialog/create-cc-dist-dialog.component.html ***!
  \****************************************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = "<h1 mat-dialog-name>Custom CC Distribution</h1>\n<mat-dialog-content>\n  <mat-form-field style=\"width: 100%\">\n    <mat-label>Name</mat-label>\n    <input matInput type=\"text\" [(ngModel)]=\"ccDist.name\">\n  </mat-form-field>\n  <h2 mat-subheader>\n    Collector Channels\n    <button mat-icon-button (click)=\"addCC()\"><mat-icon>add</mat-icon></button>\n  </h2>\n  <span *ngFor=\"let cc of ccDist.ccs; index as i\">\n    <div class=\"start-end-container\">\n      <b matPrefix>{{ i + 1 }})</b> &theta; = <input class=\"input-inline\" matInput type=\"number\"  size=\"4\" [(ngModel)]=\"cc.loc\">&deg;, G<sub>CC<sub>{{ i + 1 }}</sub></sub>/G<sub>CC<sub>avg.</sub></sub> = <input class=\"input-inline\" matInput type=\"number\" [(ngModel)]=\"cc.g_ratio\">\n      <button mat-icon-button class=\"delete-inline\" (click)=\"deleteCC(i)\"><mat-icon>clear</mat-icon></button>\n    </div>\n  </span>\n</mat-dialog-content>\n<mat-dialog-actions>\n  <button mat-button [mat-dialog-close]=\"null\">Cancel</button>\n  <button mat-button color=\"primary\" [mat-dialog-close]=\"ccDist\">Save</button>\n</mat-dialog-actions>\n"

/***/ }),

/***/ "./src/app/create-cc-dist-dialog/create-cc-dist-dialog.component.ts":
/*!**************************************************************************!*\
  !*** ./src/app/create-cc-dist-dialog/create-cc-dist-dialog.component.ts ***!
  \**************************************************************************/
/*! exports provided: CreateCcDistDialogComponent */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "CreateCcDistDialogComponent", function() { return CreateCcDistDialogComponent; });
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm5/core.js");
/* harmony import */ var _angular_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/material */ "./node_modules/@angular/material/esm5/material.es5.js");
/* harmony import */ var _simulation_cc_distribution_model__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../simulation/cc-distribution.model */ "./src/app/simulation/cc-distribution.model.ts");
/* harmony import */ var _simulation_cc_model__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../simulation/cc.model */ "./src/app/simulation/cc.model.ts");
var __decorate = (undefined && undefined.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (undefined && undefined.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};




var CreateCcDistDialogComponent = /** @class */ (function () {
    function CreateCcDistDialogComponent(dialogRef) {
        this.dialogRef = dialogRef;
        this.ccDist = new _simulation_cc_distribution_model__WEBPACK_IMPORTED_MODULE_2__["CCDistribution"]('Custom CC Distribution', []);
    }
    CreateCcDistDialogComponent.prototype.onNoClick = function () {
        this.dialogRef.close();
    };
    CreateCcDistDialogComponent.prototype.addCC = function () {
        this.ccDist.ccs.push(new _simulation_cc_model__WEBPACK_IMPORTED_MODULE_3__["CC"]());
    };
    CreateCcDistDialogComponent.prototype.deleteCC = function (i) {
        this.ccDist.ccs.splice(i, 1);
    };
    CreateCcDistDialogComponent = __decorate([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_0__["Component"])({
            selector: 'app-create-cc-dist',
            template: __webpack_require__(/*! ./create-cc-dist-dialog.component.html */ "./src/app/create-cc-dist-dialog/create-cc-dist-dialog.component.html"),
            styles: [__webpack_require__(/*! ./create-cc-dist-dialog.component.css */ "./src/app/create-cc-dist-dialog/create-cc-dist-dialog.component.css")]
        }),
        __metadata("design:paramtypes", [_angular_material__WEBPACK_IMPORTED_MODULE_1__["MatDialogRef"]])
    ], CreateCcDistDialogComponent);
    return CreateCcDistDialogComponent;
}());



/***/ }),

/***/ "./src/app/create-stent-dialog/create-stent-dialog.component.css":
/*!***********************************************************************!*\
  !*** ./src/app/create-stent-dialog/create-stent-dialog.component.css ***!
  \***********************************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = ".constant {\n  width: 100%;\n}\n"

/***/ }),

/***/ "./src/app/create-stent-dialog/create-stent-dialog.component.html":
/*!************************************************************************!*\
  !*** ./src/app/create-stent-dialog/create-stent-dialog.component.html ***!
  \************************************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = "<h1 mat-dialog-name>Create Stent</h1>\n<mat-dialog-content>\n  <mat-form-field class=\"constant\">\n    <mat-label>Name</mat-label>\n    <input placeholder=\"Name\" matInput type=\"text\" [(ngModel)]=\"data.name\">\n  </mat-form-field>\n  <mat-form-field class=\"constant\">\n    <mat-label>Length (&mu;m)</mat-label>\n    <input placeholder=\"Length (&mu;m)\" matInput type=\"number\" [(ngModel)]=\"data.length\">\n    <mat-icon matSuffix matTooltip=\"Length of stent in SC. Should not include inlet length.\" matTooltipPositon=\"right\">\n      help\n    </mat-icon>\n  </mat-form-field>\n  <mat-form-field class=\"constant\">\n    <mat-label>Inlet Location (&mu;m)</mat-label>\n    <input placeholder=\"Inlet Location (&mu;m)\" matInput type=\"number\" [(ngModel)]=\"data.loc_inlet\">\n    <mat-icon matSuffix matTooltip=\"Distance to the inlet from the leading edge of the stent\" matTooltipPositon=\"right\">\n      help\n    </mat-icon>\n  </mat-form-field>\n  <mat-form-field class=\"constant\">\n    <mat-label>Width (&mu;m)</mat-label>\n    <input matInput type=\"number\" [(ngModel)]=\"data.w\">\n    <mat-icon matSuffix matTooltip=\"Width of the stent channel\" matTooltipPositon=\"right\">\n      help\n    </mat-icon>\n  </mat-form-field>\n  <mat-divider></mat-divider>\n  <mat-form-field class=\"constant\">\n    <mat-label>Channel Height (&mu;m)</mat-label>\n    <input matInput type=\"number\" [(ngModel)]=\"data.hd\">\n    <mat-icon matSuffix matTooltip=\"Height of the stent channel. Leave blank if not constant(e.g. has window regions)\" matTooltipPositon=\"right\">\n      help\n    </mat-icon>\n  </mat-form-field>\n  Or\n  <mat-form-field class=\"constant\">\n    <mat-label># of Window Regions</mat-label>\n    <input matInput type=\"number\" [(ngModel)]=\"data.n_windows\">\n    <mat-icon matSuffix matTooltip=\"# of window regions the stent has. Window regions are regions in which SC is dilated by the stent, but TM flow is not blocked\" matTooltipPositon=\"right\">\n      help\n    </mat-icon>\n  </mat-form-field>\n  <mat-form-field class=\"constant\">\n    <mat-label>Window Length (&mu;m)</mat-label>\n    <input matInput type=\"number\" [(ngModel)]=\"data.l_window\">\n    <mat-icon matSuffix matTooltip=\"Length of window regions\" matTooltipPositon=\"right\">\n      help\n    </mat-icon>\n  </mat-form-field>\n  <mat-form-field class=\"constant\">\n    <mat-label>Window Height (&mu;m)</mat-label>\n    <input matInput type=\"number\" [(ngModel)]=\"data.h_window\">\n    <mat-icon matSuffix matTooltip=\"Height of the channel in window regions.\" matTooltipPositon=\"right\">\n      help\n    </mat-icon>\n  </mat-form-field>\n  <mat-form-field class=\"constant\">\n    <mat-label>Spine Length (&mu;m)</mat-label>\n    <input matInput type=\"number\" [(ngModel)]=\"data.l_spine\">\n    <mat-icon matSuffix matTooltip=\"Length of spine regions. Spine regions are modeled as dilated by the stent and having no flow through the TM\" matTooltipPositon=\"right\">\n      help\n    </mat-icon>\n  </mat-form-field>\n  <mat-form-field class=\"constant\">\n    <mat-label>Spine Height (&mu;m)</mat-label>\n    <input matInput type=\"number\" [(ngModel)]=\"data.h_spine\">\n    <mat-icon matSuffix matTooltip=\"Height of the channel in spine regions.\" matTooltipPositon=\"right\">\n      help\n    </mat-icon>\n  </mat-form-field>\n  <mat-divider></mat-divider>\n  <mat-form-field class=\"constant\">\n    <mat-label>Post-Stent Canal Height (&mu;m)</mat-label>\n    <input matInput type=\"number\" [(ngModel)]=\"data.h_after\">\n    <mat-icon matSuffix matTooltip=\"If the height of the device in the canal is significantly larger than the height of the channel through which fluid flows in the stent (eg. in the iStent inject), this is used for the canal height in the 0.6mm dilated region before and/or after the stent. If not specified, either Channel Height or Spine Height is used.\" matTooltipPositon=\"right\">\n      help\n    </mat-icon>\n  </mat-form-field>\n  <mat-form-field class=\"constant\">\n    <mat-label>G<sub>inlet</sub> (&mu;L/min/mmHg)</mat-label>\n    <input matInput type=\"number\" [(ngModel)]=\"data.g_inlet\">\n    <mat-icon matSuffix matTooltip=\"Conductance of the inlet portion of the stent. Should only be specified if &le; ~100 &mu;L/min/mmHg, ie. has significant resistance.\" matTooltipPositon=\"right\">\n      help\n    </mat-icon>\n  </mat-form-field>\n  <mat-checkbox [checked]=\"!!data.two_way\">Bidirectional</mat-checkbox>\n  <mat-icon matTooltip=\"If checked, flow is allowed to exit the stent on either side. Only relevant if Inlet Location = 0 &mu;m or Length\" matTooltipPositon=\"right\">\n    help\n  </mat-icon>\n  <mat-form-field class=\"constant\">\n    <mat-label>Channel Geometry</mat-label>\n    <mat-select [(value)]=\"data.geometry\">\n      <mat-option value=\"ellipse\">Ellipse</mat-option>\n      <mat-option value=\"rectangle\">Rectangle</mat-option>\n    </mat-select>\n    <mat-icon matSuffix matTooltip=\"Geometry of the channel of the stent. Use ellipse model for semicircular or circular channels as well as elliptical channels.\" matTooltipPositon=\"right\">\n      help\n    </mat-icon>\n  </mat-form-field>\n</mat-dialog-content>\n<mat-dialog-actions>\n  <button mat-button [mat-dialog-close]=\"null\">Cancel</button>\n  <button mat-button color=\"primary\" [mat-dialog-close]=\"data\">Save</button>\n</mat-dialog-actions>\n"

/***/ }),

/***/ "./src/app/create-stent-dialog/create-stent-dialog.component.ts":
/*!**********************************************************************!*\
  !*** ./src/app/create-stent-dialog/create-stent-dialog.component.ts ***!
  \**********************************************************************/
/*! exports provided: CreateStentDialogComponent */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "CreateStentDialogComponent", function() { return CreateStentDialogComponent; });
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm5/core.js");
/* harmony import */ var _angular_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/material */ "./node_modules/@angular/material/esm5/material.es5.js");
var __decorate = (undefined && undefined.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (undefined && undefined.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};


// import { FormControl, Validators } from "@angular/forms";
var CreateStentDialogComponent = /** @class */ (function () {
    function CreateStentDialogComponent(dialogRef) {
        this.dialogRef = dialogRef;
        this.data = {
            name: 'New Stent',
            length: null,
            loc_inlet: null,
            w: null,
            hd: null,
            n_windows: null,
            l_window: null,
            h_window: null,
            l_spine: null,
            h_spine: null,
            h_after: null,
            g_inlet: null,
            two_way: 0,
            geometry: 'ellipse'
        };
    }
    CreateStentDialogComponent.prototype.onNoClick = function () {
        this.dialogRef.close();
    };
    CreateStentDialogComponent = __decorate([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_0__["Component"])({
            selector: 'app-create-stent-dialog',
            template: __webpack_require__(/*! ./create-stent-dialog.component.html */ "./src/app/create-stent-dialog/create-stent-dialog.component.html"),
            styles: [__webpack_require__(/*! ./create-stent-dialog.component.css */ "./src/app/create-stent-dialog/create-stent-dialog.component.css")]
        }),
        __metadata("design:paramtypes", [_angular_material__WEBPACK_IMPORTED_MODULE_1__["MatDialogRef"]])
    ], CreateStentDialogComponent);
    return CreateStentDialogComponent;
}());



/***/ }),

/***/ "./src/app/edit-constants-dialog/constants.model.ts":
/*!**********************************************************!*\
  !*** ./src/app/edit-constants-dialog/constants.model.ts ***!
  \**********************************************************/
/*! exports provided: Constants */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "Constants", function() { return Constants; });
var Constants = /** @class */ (function () {
    function Constants() {
    }
    return Constants;
}());



/***/ }),

/***/ "./src/app/edit-constants-dialog/edit-constants-dialog.component.css":
/*!***************************************************************************!*\
  !*** ./src/app/edit-constants-dialog/edit-constants-dialog.component.css ***!
  \***************************************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = ".constant {\n  width: 100%;\n}\n"

/***/ }),

/***/ "./src/app/edit-constants-dialog/edit-constants-dialog.component.html":
/*!****************************************************************************!*\
  !*** ./src/app/edit-constants-dialog/edit-constants-dialog.component.html ***!
  \****************************************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = "<h1 mat-dialog-name>Edit Model Constants</h1>\n<mat-dialog-content>\n  <mat-form-field class=\"constant\">\n    <mat-label>Max Error</mat-label>\n    <input placeholder=\"Max Error\" matInput type=\"number\" [(ngModel)]=\"data.max_error\">\n    <mat-icon matSuffix matTooltip=\"Maximum acceptable residual to establish convergence. Can be used to force convergence in non-converging scenarios\" matTooltipPositon=\"right\">\n      help\n    </mat-icon>\n  </mat-form-field>\n  <mat-form-field class=\"constant\">\n    <mat-label>N</mat-label>\n    <input placeholder=\"N\" matInput type=\"number\" [(ngModel)]=\"data.n\">\n    <mat-icon matSuffix matTooltip=\"Number of CCs. Only used in determining matrix size (# of nodes = N*M), use CCs to control actual number of CCs\" matTooltipPositon=\"right\">\n      help\n    </mat-icon>\n  </mat-form-field>\n  <mat-form-field class=\"constant\">\n    <mat-label>M</mat-label>\n    <input placeholder=\"M\" matInput type=\"number\" [(ngModel)]=\"data.m\">\n    <mat-icon matSuffix matTooltip=\"Number of nodes between CCs (default 40). Only used in determining matrix size (# of nodes = N*M)\" matTooltipPositon=\"right\">\n      help\n    </mat-icon>\n  </mat-form-field>\n  <mat-form-field class=\"constant\">\n    <mat-label>E<sub>TM</sub> (mmHg)</mat-label>\n    <input matInput type=\"number\" [(ngModel)]=\"data.etm\">\n    <mat-icon matSuffix matTooltip=\"Young's modulus of TM\" matTooltipPositon=\"right\">\n      help\n    </mat-icon>\n  </mat-form-field>\n  <mat-form-field class=\"constant\">\n    <mat-label>R<sub>TM</sub> (mmHg/&mu;L/min)</mat-label>\n    <input matInput type=\"number\" [(ngModel)]=\"data.rtm\">\n    <mat-icon matSuffix=\"\" matTooltip=\"Overall resistance of TM\" matTooltipPositon=\"right\">\n      help\n    </mat-icon>\n  </mat-form-field>\n  <mat-form-field class=\"constant\">\n    <mat-label>K<sub>SC</sub> (mmHg<sup>1/3</sup> &mu;m)</mat-label>\n    <input matInput type=\"number\" [(ngModel)]=\"data.ksc\">\n    <mat-icon matSuffix matTooltip=\"Stiffness of septae in SC\" matTooltipPositon=\"right\">\n      help\n    </mat-icon>\n  </mat-form-field>\n  <mat-form-field class=\"constant\">\n    <mat-label>h<sub>s</sub> (&mu;m)</mat-label>\n    <input matInput type=\"number\" [(ngModel)]=\"data.hs\">\n    <mat-icon matSuffix matTooltip=\"Height at which septae begin to support SC\" matTooltipPositon=\"right\">\n      help\n    </mat-icon>\n  </mat-form-field>\n  <mat-form-field class=\"constant\">\n    <mat-label>&beta;</mat-label>\n    <input matInput type=\"number\" [(ngModel)]=\"data.beta\">\n    <mat-icon matSuffix matTooltip=\"&beta; parameter introduced by F. Yuan et al (3.0 in their paper, default=1.0) representing decrease in CC resistance near stents. This does not match the current models predictions.\" matTooltipPositon=\"right\">\n      help\n    </mat-icon>\n  </mat-form-field>\n  <mat-form-field class=\"constant\">\n    <mat-label>R<sub>CC</sub> (mmHg/&mu;L/min)</mat-label>\n    <input matInput type=\"number\" [(ngModel)]=\"data.rcc\">\n    <mat-icon matSuffix matTooltip=\"Overall resistance of CCs. If not specified a linear relationship with IOP is used.\" matTooltipPositon=\"right\">\n      help\n    </mat-icon>\n  </mat-form-field>\n  <mat-form-field class=\"constant\">\n    <mat-label>P<sub>v</sub> (mmHg)</mat-label>\n    <input matInput type=\"number\" [(ngModel)]=\"data.pev\">\n    <mat-icon matSuffix matTooltip=\"Episcleral venous pressure\" matTooltipPositon=\"right\">\n      help\n    </mat-icon>\n  </mat-form-field>\n</mat-dialog-content>\n<mat-dialog-actions>\n  <button mat-button color=\"primary\" [mat-dialog-close]=\"data\">Save</button>\n</mat-dialog-actions>\n"

/***/ }),

/***/ "./src/app/edit-constants-dialog/edit-constants-dialog.component.ts":
/*!**************************************************************************!*\
  !*** ./src/app/edit-constants-dialog/edit-constants-dialog.component.ts ***!
  \**************************************************************************/
/*! exports provided: EditConstantsDialogComponent */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "EditConstantsDialogComponent", function() { return EditConstantsDialogComponent; });
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm5/core.js");
/* harmony import */ var _angular_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/material */ "./node_modules/@angular/material/esm5/material.es5.js");
/* harmony import */ var _constants_model__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./constants.model */ "./src/app/edit-constants-dialog/constants.model.ts");
var __decorate = (undefined && undefined.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (undefined && undefined.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
var __param = (undefined && undefined.__param) || function (paramIndex, decorator) {
    return function (target, key) { decorator(target, key, paramIndex); }
};



// import { FormControl, Validators } from "@angular/forms";
var EditConstantsDialogComponent = /** @class */ (function () {
    function EditConstantsDialogComponent(dialogRef, data) {
        this.dialogRef = dialogRef;
        this.data = data;
    }
    EditConstantsDialogComponent.prototype.onNoClick = function () {
        this.dialogRef.close();
    };
    EditConstantsDialogComponent = __decorate([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_0__["Component"])({
            selector: 'app-edit-constants-dialog',
            template: __webpack_require__(/*! ./edit-constants-dialog.component.html */ "./src/app/edit-constants-dialog/edit-constants-dialog.component.html"),
            styles: [__webpack_require__(/*! ./edit-constants-dialog.component.css */ "./src/app/edit-constants-dialog/edit-constants-dialog.component.css")]
        }),
        __param(1, Object(_angular_core__WEBPACK_IMPORTED_MODULE_0__["Inject"])(_angular_material__WEBPACK_IMPORTED_MODULE_1__["MAT_DIALOG_DATA"])),
        __metadata("design:paramtypes", [_angular_material__WEBPACK_IMPORTED_MODULE_1__["MatDialogRef"],
            _constants_model__WEBPACK_IMPORTED_MODULE_2__["Constants"]])
    ], EditConstantsDialogComponent);
    return EditConstantsDialogComponent;
}());



/***/ }),

/***/ "./src/app/env.ts":
/*!************************!*\
  !*** ./src/app/env.ts ***!
  \************************/
/*! exports provided: API_URL */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "API_URL", function() { return API_URL; });
var API_URL = 'http://127.0.0.1:5000';


/***/ }),

/***/ "./src/app/sidenav/sidenav.component.css":
/*!***********************************************!*\
  !*** ./src/app/sidenav/sidenav.component.css ***!
  \***********************************************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = ".sidenav-container {\n  height: 100%;\n}\n\n.sidenav {\n  width: 200px;\n  z-index: 1000;\n\n}\n\n.mat-toolbar.mat-primary {\n  position: -webkit-sticky;\n  position: sticky;\n  top: 0;\n  z-index: 1000;\n}\n"

/***/ }),

/***/ "./src/app/sidenav/sidenav.component.html":
/*!************************************************!*\
  !*** ./src/app/sidenav/sidenav.component.html ***!
  \************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = "<mat-sidenav-container class=\"sidenav-container\">\n  <mat-sidenav\n    #drawer\n    class=\"sidenav\"\n    fixedInViewport=\"true\"\n    [attr.role]=\"(isHandset$ | async) ? 'dialog' : 'navigation'\"\n    [mode]=\"(isHandset$ | async) ? 'over' : 'side'\"\n    [opened]=\"!(isHandset$ | async)\">\n    <mat-toolbar color=\"primary\">Menu</mat-toolbar>\n    <mat-nav-list>\n      <a mat-list-item href=\"conditions\">Simulations</a>\n      <a mat-list-item href=\"new_stent\">Create a New Stent</a>\n      <a mat-list-item href=\"\">Link 3</a>\n    </mat-nav-list>\n  </mat-sidenav>\n  <mat-sidenav-content>\n    <mat-toolbar color=\"primary\">\n      <button\n        type=\"button\"\n        aria-label=\"Toggle sidenav\"\n        mat-icon-button\n        (click)=\"drawer.toggle()\"\n        *ngIf=\"isHandset$ | async\">\n        <mat-icon aria-label=\"Side nav toggle icon\">menu</mat-icon>\n      </button>\n      <span>{{ name }}</span>\n    </mat-toolbar>\n    <router-outlet></router-outlet>\n  </mat-sidenav-content>\n</mat-sidenav-container>\n"

/***/ }),

/***/ "./src/app/sidenav/sidenav.component.ts":
/*!**********************************************!*\
  !*** ./src/app/sidenav/sidenav.component.ts ***!
  \**********************************************/
/*! exports provided: SidenavComponent */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "SidenavComponent", function() { return SidenavComponent; });
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm5/core.js");
/* harmony import */ var _angular_cdk_layout__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/cdk/layout */ "./node_modules/@angular/cdk/esm5/layout.es5.js");
/* harmony import */ var rxjs_operators__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! rxjs/operators */ "./node_modules/rxjs/_esm5/operators/index.js");
var __decorate = (undefined && undefined.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (undefined && undefined.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};



var SidenavComponent = /** @class */ (function () {
    function SidenavComponent(breakpointObserver) {
        this.breakpointObserver = breakpointObserver;
        this.isHandset$ = this.breakpointObserver.observe(_angular_cdk_layout__WEBPACK_IMPORTED_MODULE_1__["Breakpoints"].Handset)
            .pipe(Object(rxjs_operators__WEBPACK_IMPORTED_MODULE_2__["map"])(function (result) { return result.matches; }));
    }
    SidenavComponent = __decorate([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_0__["Component"])({
            selector: 'app-sidenav',
            template: __webpack_require__(/*! ./sidenav.component.html */ "./src/app/sidenav/sidenav.component.html"),
            styles: [__webpack_require__(/*! ./sidenav.component.css */ "./src/app/sidenav/sidenav.component.css")]
        }),
        __metadata("design:paramtypes", [_angular_cdk_layout__WEBPACK_IMPORTED_MODULE_1__["BreakpointObserver"]])
    ], SidenavComponent);
    return SidenavComponent;
}());



/***/ }),

/***/ "./src/app/simulation/cc-distribution.model.ts":
/*!*****************************************************!*\
  !*** ./src/app/simulation/cc-distribution.model.ts ***!
  \*****************************************************/
/*! exports provided: CCDistribution */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "CCDistribution", function() { return CCDistribution; });
var CCDistribution = /** @class */ (function () {
    function CCDistribution(name, ccs) {
        this.name = name;
        this.ccs = ccs;
    }
    return CCDistribution;
}());



/***/ }),

/***/ "./src/app/simulation/cc.model.ts":
/*!****************************************!*\
  !*** ./src/app/simulation/cc.model.ts ***!
  \****************************************/
/*! exports provided: CC */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "CC", function() { return CC; });
var CC = /** @class */ (function () {
    function CC(loc, g_ratio) {
        if (loc) {
            this.loc = loc;
        }
        if (g_ratio) {
            this.g_ratio = g_ratio;
        }
    }
    return CC;
}());



/***/ }),

/***/ "./src/app/simulation/simulation.component.css":
/*!*****************************************************!*\
  !*** ./src/app/simulation/simulation.component.css ***!
  \*****************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = ".simulation-card {\n  max-width: 500px;\n  min-width: -webkit-fit-content;\n  min-width: -moz-fit-content;\n  min-width: fit-content;\n  margin: 1%;\n  z-index: 0;\n}\n\n.condition {\n  width: 100%;\n}\n\nmat-checkbox {\n  margin-bottom: 5%;\n}\n\n.surgery {\n  margin-bottom: 0px;\n  margin-top: 0px;\n}\n\n.start-end-container {\n  justify-content: space-between;\n  vertical-align: center;\n}\n\n.input-inline {\n  width: 20%;\n  text-align: right;\n  vertical-align: middle;\n\n}\n\n.select-inline {\n  width: 40%;\n  vertical-align: middle;\n}\n"

/***/ }),

/***/ "./src/app/simulation/simulation.component.html":
/*!******************************************************!*\
  !*** ./src/app/simulation/simulation.component.html ***!
  \******************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = "<mat-card class=\"simulation-card\" tabindex=\"0\">\n  <mat-card-header>\n    <app-visual-editor [(conditions)]=\"conditions\"></app-visual-editor>\n    <mat-card-name><h2>Conditions</h2></mat-card-name>\n  </mat-card-header>\n  <mat-card-content>\n    <mat-form-field class=\"condition\">\n      <mat-select placeholder=\"Mode\" [(value)]=\"conditions.mode\">\n        <mat-option value=\"constant pressure\">Constant Pressure</mat-option>\n        <mat-option value=\"constant flow\">Constant Flow</mat-option>\n      </mat-select>\n    </mat-form-field>\n    <mat-form-field class=\"condition\" *ngIf=\"conditions.mode=='constant pressure'\">\n      <input matInput placeholder=\"Intraocular Pressure (mmHg)\" type=\"number\" [(ngModel)]=\"conditions.iop\">\n    </mat-form-field>\n    <mat-form-field class=\"condition\" *ngIf=\"conditions.mode=='constant flow'\">\n      <input matInput placeholder=\"Flowrate (&mu;L/min)\" type=\"number\" [(ngModel)]=\"conditions.qt\">\n    </mat-form-field>\n    <mat-form-field class=\"condition\">\n      <mat-select placeholder=\"SC Geometry\" [(value)]=\"conditions.geometry\">\n        <mat-option value=\"ellipse\">Ellipse</mat-option>\n        <mat-option value=\"rectangle\">Rectangle</mat-option>\n      </mat-select>\n    </mat-form-field>\n    <mat-checkbox class=\"condition\" [(ngModel)]=\"conditions.glaucoma\" matTooltip=\"Toggles TM resistance between 2.0 mmHg/&mu;L/min and 7.0 mmHg/&mu;L/min. Overridden by Rtm property (Edit Constants)\">\n      Glaucomatous\n    </mat-checkbox>\n    <mat-form-field class=\"condition\">\n      <mat-select placeholder=\"CC Distribution\" [(value)]=\"conditions.ccs\">\n        <mat-option *ngFor=\"let ccDist of ccDists\" [value]=\"ccDist.ccs\">{{ ccDist.name }}</mat-option>\n        <mat-option (click)=\"addCCDist()\">Custom</mat-option>\n      </mat-select>\n    </mat-form-field>\n    <h3>Surgeries</h3>\n    <h4 class=\"surgery\">\n      Trabeculotomies\n        <button mat-icon-button (click)=\"addTrabeculotomy()\">\n          <mat-icon>add</mat-icon>\n        </button>\n      </h4>\n      <span *ngFor=\"let trab of conditions.trabeculotomies; index as i\">\n        <div class=\"start-end-container\">\n          From &theta; = <input class=\"input-inline\" matInput type=\"number\"  size=\"4\" [(ngModel)]=\"trab.start\">&deg;\n          to &theta; = <input class=\"input-inline\" matInput type=\"number\" size=\"4\" [(ngModel)]=\"trab.end\">&deg;\n          <button mat-icon-button class=\"delete-inline\" (click)=\"deleteTrabeculotomy(i)\"><mat-icon>clear</mat-icon></button>\n        </div>\n      </span>\n      <h4 class=\"surgery\">\n        Sinusotomies\n        <button mat-icon-button (click)=\"addSinusotomy()\">\n          <mat-icon>add</mat-icon>\n        </button>\n      </h4>\n      <span *ngFor=\"let sinus of conditions.sinusotomies; index as i\">\n        <div class=\"start-end-container\">\n          From &theta; = <input class=\"input-inline\" matInput type=\"number\"  size=\"4\" [(ngModel)]=\"sinus.start\">&deg;\n          to &theta; = <input class=\"input-inline\" matInput type=\"number\" size=\"4\" [(ngModel)]=\"sinus.end\">&deg;\n          <button mat-icon-button class=\"delete-inline\" (click)=\"deleteSinusotomy(i)\"><mat-icon>clear</mat-icon></button>\n        </div>\n      </span>\n      <h4 class=\"surgery\">\n        Nd:YAG Laser Holes\n        <button mat-icon-button (click)=\"addYagHole()\"><mat-icon>add</mat-icon></button>\n      </h4>\n      <span *ngFor=\"let hole of conditions.yag_holes; index as i\">\n        <div class=\"start-end-container\">\n          &theta; = <input class=\"input-inline\" matInput type=\"number\"  size=\"4\" [(ngModel)]=\"hole.loc\">&deg;\n          <button mat-icon-button class=\"delete-inline\" (click)=\"deleteYagHole(i)\"><mat-icon>clear</mat-icon></button>\n        </div>\n      </span>\n      <h4 class=\"surgery\">\n        Stents\n        <button mat-icon-button (click)=\"addStent()\"><mat-icon>add</mat-icon></button>\n      </h4>\n      <span *ngFor=\"let stent of conditions.stents; index as i\">\n        <mat-select class=\"select-inline\" placeholder=\"Stent Type\" [(value)]=\"stent.stent\">\n          <mat-option *ngFor=\"let s of stentOptions\" [value]=\"s\">{{ s.name }}</mat-option>\n          <mat-option (click)=\"newStent(i)\">New Stent</mat-option>\n        </mat-select>\n        at &theta; = <input class=\"input-inline\" matInput type=\"number\" size=\"4\" [(ngModel)]=\"stent.loc\">&deg;\n        <button mat-icon-button class=\"delete-inline\" (click)=\"deleteStent(i)\"><mat-icon>clear</mat-icon></button>\n      </span>\n  </mat-card-content>\n  <mat-card-actions>\n    <button mat-button (click)=\"editParams()\">Edit Constants</button>\n    <button mat-button color=\"primary\" (click)=\"solve()\">Solve</button>\n  </mat-card-actions>\n</mat-card>\n"

/***/ }),

/***/ "./src/app/simulation/simulation.component.ts":
/*!****************************************************!*\
  !*** ./src/app/simulation/simulation.component.ts ***!
  \****************************************************/
/*! exports provided: SimulationComponent */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "SimulationComponent", function() { return SimulationComponent; });
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm5/core.js");
/* harmony import */ var _angular_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/material */ "./node_modules/@angular/material/esm5/material.es5.js");
/* harmony import */ var _edit_constants_dialog_edit_constants_dialog_component__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../edit-constants-dialog/edit-constants-dialog.component */ "./src/app/edit-constants-dialog/edit-constants-dialog.component.ts");
/* harmony import */ var _trabeculotomy_model__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./trabeculotomy.model */ "./src/app/simulation/trabeculotomy.model.ts");
/* harmony import */ var _sinusotomy_model__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./sinusotomy.model */ "./src/app/simulation/sinusotomy.model.ts");
/* harmony import */ var _yag_hole_model__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./yag-hole.model */ "./src/app/simulation/yag-hole.model.ts");
/* harmony import */ var _stent_model__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./stent.model */ "./src/app/simulation/stent.model.ts");
/* harmony import */ var _stent_info_model__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./stent-info.model */ "./src/app/simulation/stent-info.model.ts");
/* harmony import */ var _solver_service__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ../solver.service */ "./src/app/solver.service.ts");
/* harmony import */ var _solution_model__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ../solution.model */ "./src/app/solution.model.ts");
/* harmony import */ var _create_cc_dist_dialog_create_cc_dist_dialog_component__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! ../create-cc-dist-dialog/create-cc-dist-dialog.component */ "./src/app/create-cc-dist-dialog/create-cc-dist-dialog.component.ts");
/* harmony import */ var _cc_distribution_model__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! ./cc-distribution.model */ "./src/app/simulation/cc-distribution.model.ts");
/* harmony import */ var _create_stent_dialog_create_stent_dialog_component__WEBPACK_IMPORTED_MODULE_12__ = __webpack_require__(/*! ../create-stent-dialog/create-stent-dialog.component */ "./src/app/create-stent-dialog/create-stent-dialog.component.ts");
var __decorate = (undefined && undefined.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (undefined && undefined.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};













var SimulationComponent = /** @class */ (function () {
    function SimulationComponent(dialog, solverService) {
        this.dialog = dialog;
        this.solverService = solverService;
        this.default_cc_dist = new _cc_distribution_model__WEBPACK_IMPORTED_MODULE_11__["CCDistribution"]('Default', []);
        this.ccDists = [
            new _cc_distribution_model__WEBPACK_IMPORTED_MODULE_11__["CCDistribution"]('Default', null)
        ];
        // @ts-ignore
        this.conditions = {
            mode: 'constant pressure',
            iop: 7.0,
            qt: 2.0,
            geometry: 'ellipse',
            glaucoma: false,
            trabeculotomies: [{ start: 0, end: 30 }],
            sinusotomies: [],
            yag_holes: [],
            stents: [],
            ccs: null,
            constants: {
                max_error: 1e-4,
                n: 30,
                m: 40,
                etm: 30.0,
                rtm: 2.0,
                ksc: 5.0,
                hs: 2.4,
                beta: 1.0,
                pev: 0.0
            }
        };
        this.solution = new _solution_model__WEBPACK_IMPORTED_MODULE_9__["Solution"]();
        this.stentOptions = [
            new _stent_info_model__WEBPACK_IMPORTED_MODULE_7__["StentInfo"]('iStent G1 (R)', 1000.0, 0.0, 120.0, 60.0, undefined, undefined, undefined, undefined, undefined, undefined, undefined, 1),
            new _stent_info_model__WEBPACK_IMPORTED_MODULE_7__["StentInfo"]('iStent inject', 145.0, 75.0, 50.0, 50.0, undefined, undefined, undefined, undefined, undefined, 150.0, 42.15134797, 1)
        ];
    }
    SimulationComponent.prototype.ngOnInit = function () {
    };
    SimulationComponent.prototype.addCCDist = function () {
        var _this = this;
        var dialogRef = this.dialog.open(_create_cc_dist_dialog_create_cc_dist_dialog_component__WEBPACK_IMPORTED_MODULE_10__["CreateCcDistDialogComponent"]);
        dialogRef.afterClosed().subscribe(function (result) {
            console.log('The dialog was closed');
            if (result != null) {
                _this.ccDists.push(result);
                _this.conditions.ccs = result.ccs;
            }
        });
    };
    SimulationComponent.prototype.addTrabeculotomy = function () {
        this.conditions.trabeculotomies.push(new _trabeculotomy_model__WEBPACK_IMPORTED_MODULE_3__["Trabeculotomy"]());
    };
    SimulationComponent.prototype.deleteTrabeculotomy = function (i) {
        this.conditions.trabeculotomies.splice(i, 1);
    };
    SimulationComponent.prototype.addSinusotomy = function () {
        this.conditions.sinusotomies.push(new _sinusotomy_model__WEBPACK_IMPORTED_MODULE_4__["Sinusotomy"]());
    };
    SimulationComponent.prototype.deleteSinusotomy = function (i) {
        this.conditions.sinusotomies.splice(i, 1);
    };
    SimulationComponent.prototype.addYagHole = function () {
        this.conditions.yag_holes.push(new _yag_hole_model__WEBPACK_IMPORTED_MODULE_5__["YagHole"]());
    };
    SimulationComponent.prototype.deleteYagHole = function (i) {
        this.conditions.yag_holes.splice(i, 1);
    };
    SimulationComponent.prototype.addStent = function () {
        this.conditions.stents.push(new _stent_model__WEBPACK_IMPORTED_MODULE_6__["Stent"]());
    };
    SimulationComponent.prototype.deleteStent = function (i) {
        this.conditions.stents.splice(i, 1);
    };
    SimulationComponent.prototype.newStent = function (i) {
        var _this = this;
        var dialogRef = this.dialog.open(_create_stent_dialog_create_stent_dialog_component__WEBPACK_IMPORTED_MODULE_12__["CreateStentDialogComponent"]);
        dialogRef.afterClosed().subscribe(function (result) {
            console.log('The dialog was closed');
            if (result != null) {
                _this.stentOptions.push(result);
                _this.conditions.stents[i].stent = result;
            }
        });
    };
    SimulationComponent.prototype.editParams = function () {
        var _this = this;
        var dialogRef = this.dialog.open(_edit_constants_dialog_edit_constants_dialog_component__WEBPACK_IMPORTED_MODULE_2__["EditConstantsDialogComponent"], {
            data: this.conditions.constants
        });
        dialogRef.afterClosed().subscribe(function (result) {
            console.log('The dialog was closed');
            if (result != null) {
                _this.conditions.constants = result;
            }
        });
    };
    SimulationComponent.prototype.solve = function () {
        var _this = this;
        this.solverService.solve(this.conditions)
            .subscribe(function (solution) {
            _this.solution = solution;
        });
    };
    SimulationComponent = __decorate([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_0__["Component"])({
            selector: 'app-simulation',
            template: __webpack_require__(/*! ./simulation.component.html */ "./src/app/simulation/simulation.component.html"),
            styles: [__webpack_require__(/*! ./simulation.component.css */ "./src/app/simulation/simulation.component.css")]
        }),
        __metadata("design:paramtypes", [_angular_material__WEBPACK_IMPORTED_MODULE_1__["MatDialog"], _solver_service__WEBPACK_IMPORTED_MODULE_8__["SolverService"]])
    ], SimulationComponent);
    return SimulationComponent;
}());



/***/ }),

/***/ "./src/app/simulation/sinusotomy.model.ts":
/*!************************************************!*\
  !*** ./src/app/simulation/sinusotomy.model.ts ***!
  \************************************************/
/*! exports provided: Sinusotomy */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "Sinusotomy", function() { return Sinusotomy; });
var Sinusotomy = /** @class */ (function () {
    function Sinusotomy() {
    }
    return Sinusotomy;
}());



/***/ }),

/***/ "./src/app/simulation/stent-info.model.ts":
/*!************************************************!*\
  !*** ./src/app/simulation/stent-info.model.ts ***!
  \************************************************/
/*! exports provided: StentInfo */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "StentInfo", function() { return StentInfo; });
var StentInfo = /** @class */ (function () {
    function StentInfo(name, length, loc_inlet, w, hd, n_windows, l_window, h_window, l_spine, h_spine, h_after, g_inlet, two_way, geometry) {
        this.name = name;
        this.length = length;
        this.loc_inlet = loc_inlet;
        this.w = w;
        if (hd) {
            this.hd = hd;
        }
        else if (!n_windows || !l_window || !h_window || !l_spine || !h_spine) {
            try {
                throw new Error('n_windows, l_window, h_window, l_spine, and h_spine must be defined if hd is not defined');
            }
            catch (e) {
                console.log(e);
            }
        }
        if (n_windows) {
            this.n_windows = n_windows;
        }
        else if (!hd) {
            try {
                throw new Error('hd must be defined if n_windows is not defined');
            }
            catch (e) {
                console.log(e);
            }
        }
        if (l_window) {
            this.l_window = l_window;
        }
        else if (!hd) {
            try {
                throw new Error('hd must be defined if l_window is not defined');
            }
            catch (e) {
                console.log(e);
            }
        }
        if (h_window) {
            this.h_window = h_window;
        }
        else if (!hd) {
            try {
                throw new Error('hd must be defined if h_window is not defined');
            }
            catch (e) {
                console.log(e);
            }
        }
        if (l_spine) {
            this.l_spine = l_spine;
        }
        else if (!hd) {
            try {
                throw new Error('hd must be defined if l_spine is not defined');
            }
            catch (e) {
                console.log(e);
            }
        }
        if (h_spine) {
            this.h_spine = h_spine;
        }
        else if (!hd) {
            try {
                throw new Error('hd must be defined if h_spine is not defined');
            }
            catch (e) {
                console.log(e);
            }
        }
        if (h_after) {
            this.h_after = h_after;
        }
        if (g_inlet) {
            this.g_inlet = g_inlet;
        }
        if (two_way) {
            this.two_way = two_way;
        }
        if (geometry) {
            this.geometry = geometry;
        }
        else {
            this.geometry = 'ellipse';
        }
    }
    return StentInfo;
}());



/***/ }),

/***/ "./src/app/simulation/stent.model.ts":
/*!*******************************************!*\
  !*** ./src/app/simulation/stent.model.ts ***!
  \*******************************************/
/*! exports provided: Stent */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "Stent", function() { return Stent; });
var Stent = /** @class */ (function () {
    function Stent() {
    }
    return Stent;
}());



/***/ }),

/***/ "./src/app/simulation/trabeculotomy.model.ts":
/*!***************************************************!*\
  !*** ./src/app/simulation/trabeculotomy.model.ts ***!
  \***************************************************/
/*! exports provided: Trabeculotomy */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "Trabeculotomy", function() { return Trabeculotomy; });
var Trabeculotomy = /** @class */ (function () {
    function Trabeculotomy() {
    }
    return Trabeculotomy;
}());



/***/ }),

/***/ "./src/app/simulation/yag-hole.model.ts":
/*!**********************************************!*\
  !*** ./src/app/simulation/yag-hole.model.ts ***!
  \**********************************************/
/*! exports provided: YagHole */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "YagHole", function() { return YagHole; });
var YagHole = /** @class */ (function () {
    function YagHole() {
    }
    return YagHole;
}());



/***/ }),

/***/ "./src/app/solution.model.ts":
/*!***********************************!*\
  !*** ./src/app/solution.model.ts ***!
  \***********************************/
/*! exports provided: Solution */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "Solution", function() { return Solution; });
var Solution = /** @class */ (function () {
    function Solution() {
    }
    return Solution;
}());



/***/ }),

/***/ "./src/app/solver.service.ts":
/*!***********************************!*\
  !*** ./src/app/solver.service.ts ***!
  \***********************************/
/*! exports provided: SolverService */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "SolverService", function() { return SolverService; });
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm5/core.js");
/* harmony import */ var rxjs__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! rxjs */ "./node_modules/rxjs/_esm5/index.js");
/* harmony import */ var _angular_common_http__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @angular/common/http */ "./node_modules/@angular/common/fesm5/http.js");
/* harmony import */ var _env__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./env */ "./src/app/env.ts");
/* harmony import */ var rxjs_operators__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! rxjs/operators */ "./node_modules/rxjs/_esm5/operators/index.js");
var __decorate = (undefined && undefined.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (undefined && undefined.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};





var SolverService = /** @class */ (function () {
    function SolverService(http) {
        this.http = http;
    }
    SolverService.prototype.handleError = function (error) {
        if (error.error instanceof ErrorEvent) {
            console.error('An error occurred:', error.error.message);
        }
        else {
            console.error('Backend returned code ${error.status}, ' +
                'body was: ${error.error}');
        }
        return Object(rxjs__WEBPACK_IMPORTED_MODULE_1__["throwError"])('Something bad happened; please try again later.');
    };
    ;
    SolverService.prototype.solve = function (conditions) {
        return this.http.post(_env__WEBPACK_IMPORTED_MODULE_3__["API_URL"] + "/solve", conditions)
            .pipe(Object(rxjs_operators__WEBPACK_IMPORTED_MODULE_4__["catchError"])(this.handleError));
    };
    SolverService.prototype.getPressureDist = function (conditions) {
        return this.http.post(_env__WEBPACK_IMPORTED_MODULE_3__["API_URL"] + "/pressure_dist", conditions)
            .pipe(Object(rxjs_operators__WEBPACK_IMPORTED_MODULE_4__["catchError"])(this.handleError));
    };
    SolverService.prototype.getHeightDist = function (conditions) {
        return this.http.post(_env__WEBPACK_IMPORTED_MODULE_3__["API_URL"] + "/height_dist", conditions)
            .pipe(Object(rxjs_operators__WEBPACK_IMPORTED_MODULE_4__["catchError"])(this.handleError));
    };
    SolverService = __decorate([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_0__["Injectable"])({
            providedIn: 'root'
        }),
        __metadata("design:paramtypes", [_angular_common_http__WEBPACK_IMPORTED_MODULE_2__["HttpClient"]])
    ], SolverService);
    return SolverService;
}());



/***/ }),

/***/ "./src/app/surgery-arc/surgery-arc.component.html":
/*!********************************************************!*\
  !*** ./src/app/surgery-arc/surgery-arc.component.html ***!
  \********************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = "<svg height=\"600\" width=\"600\">\n  <g>\n    <line #start [attr.x1]=\"circle.centerX\" [attr.y1]=\"circle.centerY\" [attr.x2]=\"arc.x1\" [attr.y2]=\"arc.y1\"></line>\n    <path #segment [attr.d]=\"d\" [attr.color]=\"color\" [attr.stroke-width]=\"circle.strokeWidth\"></path>\n    <line #stop [attr.x1]=\"circle.centerX\" [attr.y1]=\"circle.centerY\" [attr.x2]=\"arc.x2\" [attr.y2]=\"arc.y2\"></line>\n  </g>\n</svg>\n"

/***/ }),

/***/ "./src/app/surgery-arc/surgery-arc.component.scss":
/*!********************************************************!*\
  !*** ./src/app/surgery-arc/surgery-arc.component.scss ***!
  \********************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = ""

/***/ }),

/***/ "./src/app/surgery-arc/surgery-arc.component.ts":
/*!******************************************************!*\
  !*** ./src/app/surgery-arc/surgery-arc.component.ts ***!
  \******************************************************/
/*! exports provided: SurgeryArcComponent */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "SurgeryArcComponent", function() { return SurgeryArcComponent; });
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm5/core.js");
/* harmony import */ var rxjs__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! rxjs */ "./node_modules/rxjs/_esm5/index.js");
/* harmony import */ var rxjs_operators__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! rxjs/operators */ "./node_modules/rxjs/_esm5/operators/index.js");
var __decorate = (undefined && undefined.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (undefined && undefined.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};



var THROTTLE_DEFAULT = 50;
var SurgeryArcComponent = /** @class */ (function () {
    function SurgeryArcComponent() {
        this.arcChange = new _angular_core__WEBPACK_IMPORTED_MODULE_0__["EventEmitter"]();
    }
    SurgeryArcComponent_1 = SurgeryArcComponent;
    Object.defineProperty(SurgeryArcComponent.prototype, "arc", {
        get: function () {
            return this.arcValue;
        },
        set: function (val) {
            this.arcValue = val;
            this.arcChange.emit(this.arcValue);
        },
        enumerable: true,
        configurable: true
    });
    SurgeryArcComponent.extractMouseEventCoords = function (e) {
        var coords = e instanceof MouseEvent
            ? {
                x: e.clientX,
                y: e.clientY
            }
            : {
                x: e.changedTouches.item(0).clientX,
                y: e.changedTouches.item(0).clientY
            };
        return coords;
    };
    SurgeryArcComponent.prototype.ngOnInit = function () {
        this.setObservables();
        this.setPathParams();
    };
    SurgeryArcComponent.prototype.ngOnChanges = function () {
        this.setPathParams();
    };
    SurgeryArcComponent.prototype.ngOnDestroy = function () {
        this.closeStreams();
    };
    SurgeryArcComponent.prototype.setObservables = function () {
        var _this = this;
        var mouseMove$ = Object(rxjs__WEBPACK_IMPORTED_MODULE_1__["merge"])(Object(rxjs__WEBPACK_IMPORTED_MODULE_1__["fromEvent"])(document, "mousemove"), Object(rxjs__WEBPACK_IMPORTED_MODULE_1__["fromEvent"])(document, "touchmove"));
        var mouseUp$ = Object(rxjs__WEBPACK_IMPORTED_MODULE_1__["merge"])(Object(rxjs__WEBPACK_IMPORTED_MODULE_1__["fromEvent"])(document, "mouseup"), Object(rxjs__WEBPACK_IMPORTED_MODULE_1__["fromEvent"])(document, "touchend"));
        this.startSubscription = Object(rxjs__WEBPACK_IMPORTED_MODULE_1__["merge"])(Object(rxjs__WEBPACK_IMPORTED_MODULE_1__["fromEvent"])(this.start.nativeElement, "touchstart"), Object(rxjs__WEBPACK_IMPORTED_MODULE_1__["fromEvent"])(this.start.nativeElement, "mousedown"))
            .pipe(Object(rxjs_operators__WEBPACK_IMPORTED_MODULE_2__["switchMap"])(function (_) {
            return mouseMove$.pipe(Object(rxjs_operators__WEBPACK_IMPORTED_MODULE_2__["takeUntil"])(mouseUp$), Object(rxjs_operators__WEBPACK_IMPORTED_MODULE_2__["throttleTime"])(THROTTLE_DEFAULT));
        }))
            .subscribe(function (res) {
            _this.handleStartPan(res);
        });
        this.stopSubscription = Object(rxjs__WEBPACK_IMPORTED_MODULE_1__["merge"])(Object(rxjs__WEBPACK_IMPORTED_MODULE_1__["fromEvent"])(this.stop.nativeElement, "touchstart"), Object(rxjs__WEBPACK_IMPORTED_MODULE_1__["fromEvent"])(this.stop.nativeElement, "mousedown"))
            .pipe(Object(rxjs_operators__WEBPACK_IMPORTED_MODULE_2__["switchMap"])(function (_) {
            return mouseMove$.pipe(Object(rxjs_operators__WEBPACK_IMPORTED_MODULE_2__["takeUntil"])(mouseUp$), Object(rxjs_operators__WEBPACK_IMPORTED_MODULE_2__["throttleTime"])(THROTTLE_DEFAULT));
        }))
            .subscribe(function (res) {
            _this.handleStopPan(res);
        });
    };
    SurgeryArcComponent.prototype.closeStreams = function () {
        if (this.startSubscription) {
            this.startSubscription.unsubscribe();
            this.startSubscription = null;
        }
        if (this.stopSubscription) {
            this.stopSubscription.unsubscribe();
            this.stopSubscription = null;
        }
    };
    SurgeryArcComponent.prototype.handleStartPan = function (e) {
        var coords = SurgeryArcComponent_1.extractMouseEventCoords(e);
        var newAngle = Math.atan2(coords.y - this.circle.centerY, coords.x - this.circle.centerX) % (2 * Math.PI);
        if (newAngle < 0) {
            newAngle += 2 * Math.PI;
        }
        this.arc.x1 = this.circle.radius * Math.cos(newAngle) + this.circle.centerX;
        this.arc.y1 = this.circle.radius * Math.sin(newAngle) + this.circle.centerY;
    };
    SurgeryArcComponent.prototype.handleStopPan = function (e) {
        var coords = SurgeryArcComponent_1.extractMouseEventCoords(e);
        var newAngle = Math.atan2(coords.y - this.circle.centerY, coords.x - this.circle.centerX) % (2 * Math.PI);
        if (newAngle < 0) {
            newAngle += 2 * Math.PI;
        }
        this.arc.x2 = this.circle.radius * Math.cos(newAngle) + this.circle.centerX;
        this.arc.y2 = this.circle.radius * Math.sin(newAngle) + this.circle.centerY;
    };
    SurgeryArcComponent.prototype.setPathParams = function () {
        this.d = 'M ' + this.arc.x1.toString() + ' ' + this.arc.y1.toString() + ' A ' + this.circle.radius.toString() + ' ' + this.circle.radius.toString() + ' 0 0 1 ' + this.arc.x2.toString() + ' ' + this.arc.y2.toString();
        this.color = this.arc.color;
    };
    __decorate([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_0__["Input"])(),
        __metadata("design:type", Object)
    ], SurgeryArcComponent.prototype, "circle", void 0);
    __decorate([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_0__["Output"])(),
        __metadata("design:type", _angular_core__WEBPACK_IMPORTED_MODULE_0__["EventEmitter"])
    ], SurgeryArcComponent.prototype, "arcChange", void 0);
    __decorate([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_0__["Input"])(),
        __metadata("design:type", Object),
        __metadata("design:paramtypes", [Object])
    ], SurgeryArcComponent.prototype, "arc", null);
    __decorate([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_0__["ViewChild"])("segment"),
        __metadata("design:type", _angular_core__WEBPACK_IMPORTED_MODULE_0__["ElementRef"])
    ], SurgeryArcComponent.prototype, "segment", void 0);
    __decorate([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_0__["ViewChild"])("start"),
        __metadata("design:type", _angular_core__WEBPACK_IMPORTED_MODULE_0__["ElementRef"])
    ], SurgeryArcComponent.prototype, "start", void 0);
    __decorate([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_0__["ViewChild"])("stop"),
        __metadata("design:type", _angular_core__WEBPACK_IMPORTED_MODULE_0__["ElementRef"])
    ], SurgeryArcComponent.prototype, "stop", void 0);
    SurgeryArcComponent = SurgeryArcComponent_1 = __decorate([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_0__["Component"])({
            selector: 'app-surgery-arc',
            template: __webpack_require__(/*! ./surgery-arc.component.html */ "./src/app/surgery-arc/surgery-arc.component.html"),
            styles: [__webpack_require__(/*! ./surgery-arc.component.scss */ "./src/app/surgery-arc/surgery-arc.component.scss")]
        }),
        __metadata("design:paramtypes", [])
    ], SurgeryArcComponent);
    return SurgeryArcComponent;
    var SurgeryArcComponent_1;
}());



/***/ }),

/***/ "./src/app/visual-editor/visual-editor.component.html":
/*!************************************************************!*\
  !*** ./src/app/visual-editor/visual-editor.component.html ***!
  \************************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = "<svg height=\"600\" width=\"600\">\n  <g>\n    <circle r=\"250\" stroke=\"grey\" stroke-width=\"40\" opacity=\"0.4\" fill-opacity=\"0\" cx=\"300\" cy=\"300\"></circle>\n    <app-surgery-arc *ngFor=\"let a of arcs\" [arc]=\"a\" [circle]=\"circleProps\"></app-surgery-arc>\n  </g>\n</svg>\n"

/***/ }),

/***/ "./src/app/visual-editor/visual-editor.component.scss":
/*!************************************************************!*\
  !*** ./src/app/visual-editor/visual-editor.component.scss ***!
  \************************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

module.exports = ""

/***/ }),

/***/ "./src/app/visual-editor/visual-editor.component.ts":
/*!**********************************************************!*\
  !*** ./src/app/visual-editor/visual-editor.component.ts ***!
  \**********************************************************/
/*! exports provided: VisualEditorComponent */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "VisualEditorComponent", function() { return VisualEditorComponent; });
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm5/core.js");
var __decorate = (undefined && undefined.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (undefined && undefined.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};

var DEFAULT_PROPS = {
    radius: 200,
    strokeWidth: 50,
    centerX: 225,
    centerY: 225
};
var VisualEditorComponent = /** @class */ (function () {
    function VisualEditorComponent() {
        this.conditionsChange = new _angular_core__WEBPACK_IMPORTED_MODULE_0__["EventEmitter"]();
        this.props = DEFAULT_PROPS;
    }
    Object.defineProperty(VisualEditorComponent.prototype, "conditions", {
        get: function () {
            return this.conditionsValue;
        },
        set: function (val) {
            this.conditionsValue = val;
            this.toArcs();
            this.conditionsChange.emit(this.conditionsValue);
        },
        enumerable: true,
        configurable: true
    });
    VisualEditorComponent.prototype.ngOnInit = function () {
    };
    VisualEditorComponent.prototype.ngOnChanges = function () {
        this.toArcs();
    };
    VisualEditorComponent.prototype.toArcs = function () {
        var a = [];
        if (this.conditions.trabeculotomies.length > 0) {
            for (var _i = 0, _a = this.conditions.trabeculotomies; _i < _a.length; _i++) {
                var trab = _a[_i];
                a.push({
                    x1: this.props.radius * Math.cos(trab.start) + this.props.centerX,
                    y1: this.props.radius * Math.sin(trab.start) + this.props.centerY,
                    x2: this.props.radius * Math.cos(trab.end) + this.props.centerX,
                    y2: this.props.radius * Math.sin(trab.end) + this.props.centerY,
                    color: "red"
                });
            }
        }
        if (this.conditions.sinusotomies.length > 0) {
            for (var _b = 0, _c = this.conditions.sinusotomies; _b < _c.length; _b++) {
                var sinus = _c[_b];
                a.push({
                    x1: this.props.radius * Math.cos(sinus.start) + this.props.centerX,
                    y1: this.props.radius * Math.sin(sinus.start) + this.props.centerY,
                    x2: this.props.radius * Math.cos(sinus.end) + this.props.centerX,
                    y2: this.props.radius * Math.sin(sinus.end) + this.props.centerY,
                    color: "yellow"
                });
            }
        }
        if (this.conditions.yag_holes.length > 0) {
            for (var _d = 0, _e = this.conditions.yag_holes; _d < _e.length; _d++) {
                var hole = _e[_d];
                a.push({
                    x1: this.props.radius * Math.cos(hole.loc - 0.5) + this.props.centerX,
                    y1: this.props.radius * Math.sin(hole.loc - 0.5) + this.props.centerY,
                    x2: this.props.radius * Math.cos(hole.loc + 0.5) + this.props.centerX,
                    y2: this.props.radius * Math.sin(hole.loc + 0.5) + this.props.centerY,
                    color: "orange"
                });
            }
        }
        if (this.conditions.stents.length > 0) {
            for (var _f = 0, _g = this.conditions.stents; _f < _g.length; _f++) {
                var stent = _g[_f];
                a.push({
                    x1: this.props.radius * Math.cos(stent.loc) + this.props.centerX,
                    y1: this.props.radius * Math.sin(stent.loc) + this.props.centerY,
                    x2: this.props.radius * Math.cos(stent.loc + (stent.stent.length / 100)) + this.props.centerX,
                    y2: this.props.radius * Math.sin(stent.loc + (stent.stent.length / 100)) + this.props.centerY,
                    color: "green"
                });
            }
        }
        this.arcs = a;
    };
    __decorate([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_0__["Input"])(),
        __metadata("design:type", Object)
    ], VisualEditorComponent.prototype, "props", void 0);
    __decorate([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_0__["Output"])(),
        __metadata("design:type", _angular_core__WEBPACK_IMPORTED_MODULE_0__["EventEmitter"])
    ], VisualEditorComponent.prototype, "conditionsChange", void 0);
    __decorate([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_0__["Input"])(),
        __metadata("design:type", Object),
        __metadata("design:paramtypes", [Object])
    ], VisualEditorComponent.prototype, "conditions", null);
    __decorate([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_0__["ViewChild"])("circle"),
        __metadata("design:type", _angular_core__WEBPACK_IMPORTED_MODULE_0__["ElementRef"])
    ], VisualEditorComponent.prototype, "circle", void 0);
    VisualEditorComponent = __decorate([
        Object(_angular_core__WEBPACK_IMPORTED_MODULE_0__["Component"])({
            selector: 'app-visual-editor',
            template: __webpack_require__(/*! ./visual-editor.component.html */ "./src/app/visual-editor/visual-editor.component.html"),
            styles: [__webpack_require__(/*! ./visual-editor.component.scss */ "./src/app/visual-editor/visual-editor.component.scss")]
        }),
        __metadata("design:paramtypes", [])
    ], VisualEditorComponent);
    return VisualEditorComponent;
}());



/***/ }),

/***/ "./src/environments/environment.ts":
/*!*****************************************!*\
  !*** ./src/environments/environment.ts ***!
  \*****************************************/
/*! exports provided: environment */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "environment", function() { return environment; });
// This file can be replaced during build by using the `fileReplacements` array.
// `ng build ---prod` replaces `environment.ts` with `environment.prod.ts`.
// The list of file replacements can be found in `angular.json`.
var environment = {
    production: false
};
/*
 * In development mode, for easier debugging, you can ignore zone related error
 * stack frames such as `zone.run`/`zoneDelegate.invokeTask` by importing the
 * below file. Don't forget to comment it out in production mode
 * because it will have a performance impact when errors are thrown
 */
// import 'zone.js/dist/zone-error';  // Included with Angular CLI.


/***/ }),

/***/ "./src/main.ts":
/*!*********************!*\
  !*** ./src/main.ts ***!
  \*********************/
/*! no exports provided */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @angular/core */ "./node_modules/@angular/core/fesm5/core.js");
/* harmony import */ var _angular_platform_browser_dynamic__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/platform-browser-dynamic */ "./node_modules/@angular/platform-browser-dynamic/fesm5/platform-browser-dynamic.js");
/* harmony import */ var _app_app_module__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./app/app.module */ "./src/app/app.module.ts");
/* harmony import */ var _environments_environment__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./environments/environment */ "./src/environments/environment.ts");




if (_environments_environment__WEBPACK_IMPORTED_MODULE_3__["environment"].production) {
    Object(_angular_core__WEBPACK_IMPORTED_MODULE_0__["enableProdMode"])();
}
Object(_angular_platform_browser_dynamic__WEBPACK_IMPORTED_MODULE_1__["platformBrowserDynamic"])().bootstrapModule(_app_app_module__WEBPACK_IMPORTED_MODULE_2__["AppModule"])
    .catch(function (err) { return console.log(err); });


/***/ }),

/***/ 0:
/*!************************************************************************!*\
  !*** multi (webpack)-dev-server/client?http://0.0.0.0:0 ./src/main.ts ***!
  \************************************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

__webpack_require__(/*! /Users/nickfarrar/Documents/Research/GlaucomaSurgeryModel/aqueous-outflow/frontend/node_modules/webpack-dev-server/client/index.js?http://0.0.0.0:0 */"./node_modules/webpack-dev-server/client/index.js?http://0.0.0.0:0");
module.exports = __webpack_require__(/*! /Users/nickfarrar/Documents/Research/GlaucomaSurgeryModel/aqueous-outflow/frontend/src/main.ts */"./src/main.ts");


/***/ })

},[[0,"runtime","vendor"]]]);
//# sourceMappingURL=main.js.map
