# \# Solar Intelligence Core

# 

# Local, offline-first ML and intelligence module for renewable-energy

# operations.

# 

# The current implementation is focused on \*\*solar power\*\* and converts

# measurements plus historical operating data into a structured \*\*Evidence

# Package\*\* for downstream Backend, Frontend, and AI Agent integration.

# 

# The Intelligence Core owns:

# 

# \- data validation

# \- feature engineering

# \- ML power prediction

# \- expected-vs-actual comparison

# \- anomaly detection

# \- historical comparable-condition analysis

# \- energy balance calculation

# \- cause indicators

# \- offline future power forecasting baseline

# \- operational constraint validation

# \- optimization-ready inputs

# 

# The Intelligence Core does \*\*not\*\* own:

# 

# \- root-cause conclusions

# \- natural-language diagnosis

# \- operational recommendations

# \- autonomous control decisions

# \- external LLM/API calls

# 

# Those responsibilities belong downstream to the \*\*AI Agent\*\* and product

# orchestration layers.

# 

# \---

# 

# \## Architecture

# 

# ```text

# Real-world / Historical Measurements

# &#x20;               |

# &#x20;               v

# &#x20;       Backend / Data Layer

# &#x20;               |

# &#x20;               v

# &#x20;      +--------------------+

# &#x20;      |  Intelligence Core |

# &#x20;      +--------------------+

# &#x20;               |

# &#x20;       +-------+-------+

# &#x20;       |               |

# &#x20;       v               v

# &#x20;  ML Prediction    Anomaly Detection

# &#x20;       |               |

# &#x20;       +-------+-------+

# &#x20;               |

# &#x20;               v

# &#x20;        Evidence Package

# &#x20;               |

# &#x20;      +--------+---------+

# &#x20;      |                  |

# &#x20;      v                  v

# &#x20;  AI Agent            Backend

# Root Cause +         Orchestration

# Recommendations          |

# &#x20;                        v

# &#x20;                    Frontend

