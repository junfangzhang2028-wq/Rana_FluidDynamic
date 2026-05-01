import {Solution} from "./solution.model";
import {Conditions} from "./simulation/conditions.model";

// export const API_URL = 'http://localhost:5000'
export const API_URL = 'http://aqueousoutflow.ads.northwestern.edu/api';
export const environment = {
  conditions: new Conditions('constant flow'),
  solution: new Solution(),
  solving: false,
  solved: false,
  hasSoln: false,
  failed: false,
};
