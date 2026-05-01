export class StentInfo {
  public name: string;
  public length: number;
  public loc_inlet: number;
  public w: number;
  public hd: number;
  public n_windows: number;
  public l_window: number;
  public h_window: number;
  public l_spine: number;
  public h_spine: number;
  public h_after: number;
  public g_inlet: number;
  public two_way: boolean;
  public geometry: 'ellipse' | 'rectangle';

  constructor(name: string, length: number, loc_inlet: number, w: number, hd?: number, n_windows?: number, l_window?: number, h_window?: number, l_spine?: number, h_spine?: number, h_after?: number, g_inlet?: number, two_way?: boolean, geometry?: 'ellipse' | 'rectangle') {
    this.name = name;
    this.length = length;
    this.loc_inlet = loc_inlet;
    this.w = w;
    if (hd) {
      this.hd = hd;
    } else if (!n_windows || !l_window || !h_window || !l_spine || !h_spine) {
      try {
        throw new Error('n_windows, l_window, h_window, l_spine, and h_spine must be defined if hd is not defined');
      }
      catch(e) {
        console.log(e);
      }
    }

    if (n_windows) {
      this.n_windows = n_windows;
    } else if (!hd) {
      try {
        throw new Error('hd must be defined if n_windows is not defined')
      }
      catch (e) {
        console.log(e)
      }
    }

    if (l_window) {
      this.l_window = l_window;
    } else if (!hd) {
      try {
        throw new Error('hd must be defined if l_window is not defined')
      }
      catch (e) {
        console.log(e)
      }
    }

    if (h_window) {
      this.h_window = h_window;
    } else if (!hd) {
      try {
        throw new Error('hd must be defined if h_window is not defined')
      }
      catch (e) {
        console.log(e)
      }
    }

    if (l_spine) {
      this.l_spine = l_spine;
    } else if (!hd) {
      try {
        throw new Error('hd must be defined if l_spine is not defined')
      }
      catch (e) {
        console.log(e)
      }
    }

    if (h_spine) {
      this.h_spine = h_spine;
    } else if (!hd) {
      try {
        throw new Error('hd must be defined if h_spine is not defined')
      }
      catch (e) {
        console.log(e)
      }
    }

    if (h_after) {
      this.h_after = h_after;
    }

    if (g_inlet) {
      this.g_inlet = g_inlet;
    }

    if (two_way == false || two_way == true) {
      this.two_way = two_way;
    } else if (loc_inlet != 0 || loc_inlet != length) {
      this.two_way = true;
    } else {
      this.two_way = false;
    }

    if (geometry) {
      this.geometry = geometry;
    } else {
      this.geometry = 'ellipse';
    }

  }
}
