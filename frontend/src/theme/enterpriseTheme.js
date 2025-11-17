// Enterprise SAP/ERP Theme Configuration for Ant Design
// This creates a professional, data-dense UI similar to SAP Business Suite

const enterpriseTheme = {
  token: {
    // Primary brand colors - SAP-inspired blue palette
    colorPrimary: '#0070d2',
    colorInfo: '#0070d2',
    colorSuccess: '#2e844a',
    colorWarning: '#ff9900',
    colorError: '#c23934',

    // Background colors
    colorBgContainer: '#ffffff',
    colorBgElevated: '#ffffff',
    colorBgLayout: '#f4f6f9',
    colorBgSpotlight: '#f0f2f5',

    // Border colors
    colorBorder: '#d8dde6',
    colorBorderSecondary: '#e5e8ed',

    // Text colors
    colorText: '#16325c',
    colorTextSecondary: '#54698d',
    colorTextTertiary: '#8a96a8',
    colorTextQuaternary: '#b0b6bf',

    // Typography - Professional, dense
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "SF Pro Display", Roboto, "Noto Sans", Ubuntu, Cantarell, "Helvetica Neue", sans-serif',
    fontSize: 13,
    fontSizeHeading1: 28,
    fontSizeHeading2: 24,
    fontSizeHeading3: 20,
    fontSizeHeading4: 16,
    fontSizeHeading5: 14,
    fontSizeLG: 15,
    fontSizeSM: 12,
    fontSizeXL: 18,

    // Line heights for dense information display
    lineHeight: 1.5,
    lineHeightHeading1: 1.3,
    lineHeightHeading2: 1.35,
    lineHeightHeading3: 1.4,
    lineHeightHeading4: 1.45,
    lineHeightHeading5: 1.5,

    // Border radius - More square/professional
    borderRadius: 4,
    borderRadiusLG: 6,
    borderRadiusSM: 3,
    borderRadiusXS: 2,

    // Spacing - Tighter for information density
    padding: 12,
    paddingLG: 16,
    paddingSM: 8,
    paddingXS: 4,
    paddingXXS: 2,

    margin: 12,
    marginLG: 16,
    marginSM: 8,
    marginXS: 4,
    marginXXS: 2,

    // Control heights - Standard ERP sizing
    controlHeight: 32,
    controlHeightLG: 36,
    controlHeightSM: 28,
    controlHeightXS: 24,

    // Box shadows - Subtle, professional
    boxShadow: '0 2px 8px rgba(22, 50, 92, 0.08)',
    boxShadowSecondary: '0 4px 12px rgba(22, 50, 92, 0.12)',
    boxShadowTertiary: '0 1px 2px rgba(22, 50, 92, 0.04)',

    // Motion - Fast and efficient
    motionDurationFast: '0.1s',
    motionDurationMid: '0.2s',
    motionDurationSlow: '0.3s',
  },
  components: {
    // Layout - Enterprise sidebar and header
    Layout: {
      headerBg: '#16325c',
      headerColor: '#ffffff',
      headerHeight: 48,
      headerPadding: '0 24px',
      siderBg: '#16325c',
      bodyBg: '#f4f6f9',
      footerBg: '#f4f6f9',
      triggerBg: '#0d2240',
      triggerColor: '#ffffff',
    },

    // Menu - Professional navigation
    Menu: {
      itemBg: 'transparent',
      itemColor: 'rgba(255, 255, 255, 0.85)',
      itemHoverBg: 'rgba(255, 255, 255, 0.08)',
      itemHoverColor: '#ffffff',
      itemSelectedBg: 'rgba(0, 112, 210, 0.4)',
      itemSelectedColor: '#ffffff',
      subMenuItemBg: 'rgba(0, 0, 0, 0.1)',
      darkItemBg: 'transparent',
      darkItemColor: 'rgba(255, 255, 255, 0.85)',
      darkItemHoverBg: 'rgba(255, 255, 255, 0.08)',
      darkItemHoverColor: '#ffffff',
      darkItemSelectedBg: 'rgba(0, 112, 210, 0.4)',
      darkItemSelectedColor: '#ffffff',
      darkSubMenuItemBg: 'rgba(0, 0, 0, 0.1)',
      iconSize: 16,
      fontSize: 13,
      itemHeight: 40,
      itemMarginInline: 8,
      itemPaddingInline: 16,
    },

    // Table - Data-dense enterprise grid
    Table: {
      headerBg: '#f0f2f5',
      headerColor: '#16325c',
      headerSplitColor: '#d8dde6',
      headerSortActiveBg: '#e5e8ed',
      headerSortHoverBg: '#e5e8ed',
      headerFilterHoverBg: '#e5e8ed',
      rowHoverBg: '#f5f7fa',
      rowSelectedBg: '#e8f4fd',
      rowSelectedHoverBg: '#d9ecfc',
      rowExpandedBg: '#fafafa',
      cellPaddingBlock: 10,
      cellPaddingInline: 12,
      cellFontSize: 13,
      headerBorderRadius: 0,
      footerBg: '#fafafa',
      footerColor: '#16325c',
      borderColor: '#d8dde6',
    },

    // Card - Professional panels
    Card: {
      headerBg: '#ffffff',
      headerFontSize: 14,
      headerFontSizeSM: 13,
      headerHeight: 48,
      headerHeightSM: 40,
      actionsBg: '#f9fafb',
      actionsLiMargin: '8px 0',
      tabsMarginBottom: -1,
      paddingLG: 20,
      padding: 16,
      paddingSM: 12,
    },

    // Button - Professional actions
    Button: {
      paddingInline: 16,
      paddingInlineSM: 12,
      paddingInlineLG: 20,
      contentFontSize: 13,
      contentFontSizeSM: 12,
      contentFontSizeLG: 14,
      borderRadius: 4,
      borderRadiusLG: 4,
      borderRadiusSM: 3,
      controlHeight: 32,
      controlHeightSM: 28,
      controlHeightLG: 36,
      defaultBg: '#ffffff',
      defaultBorderColor: '#d8dde6',
      defaultColor: '#16325c',
      defaultHoverBg: '#f5f7fa',
      defaultHoverBorderColor: '#b0b6bf',
      defaultHoverColor: '#16325c',
      defaultActiveBg: '#e5e8ed',
      defaultActiveBorderColor: '#8a96a8',
      defaultActiveColor: '#16325c',
      primaryColor: '#ffffff',
      dangerColor: '#ffffff',
      textHoverBg: 'rgba(0, 0, 0, 0.04)',
      ghostBg: 'transparent',
    },

    // Input - Form fields
    Input: {
      activeBg: '#ffffff',
      hoverBg: '#ffffff',
      activeBorderColor: '#0070d2',
      hoverBorderColor: '#8a96a8',
      activeShadow: '0 0 0 2px rgba(0, 112, 210, 0.2)',
      errorActiveShadow: '0 0 0 2px rgba(194, 57, 52, 0.2)',
      warningActiveShadow: '0 0 0 2px rgba(255, 153, 0, 0.2)',
      paddingBlock: 6,
      paddingBlockLG: 8,
      paddingBlockSM: 4,
      paddingInline: 10,
      paddingInlineLG: 12,
      paddingInlineSM: 8,
    },

    // Select - Dropdown fields
    Select: {
      controlItemBgActive: '#e8f4fd',
      controlItemBgHover: '#f5f7fa',
      optionActiveBg: '#e8f4fd',
      optionSelectedBg: '#e8f4fd',
      optionSelectedFontWeight: 500,
      optionFontSize: 13,
      optionHeight: 32,
      optionPadding: '6px 12px',
    },

    // Tag - Status indicators
    Tag: {
      defaultBg: '#f0f2f5',
      defaultColor: '#16325c',
      borderRadiusSM: 3,
      fontSize: 12,
      fontSizeSM: 11,
      lineHeight: 1.5,
      lineHeightSM: 1.5,
      marginXXS: 4,
    },

    // Badge - Notification dots
    Badge: {
      dotSize: 8,
      fontSize: 11,
      fontSizeSM: 10,
      textFontSize: 11,
      textFontSizeSM: 10,
      textFontWeight: 500,
    },

    // Tabs - Section navigation
    Tabs: {
      cardBg: '#f0f2f5',
      cardHeight: 40,
      cardPadding: '8px 16px',
      horizontalItemGutter: 24,
      horizontalItemPadding: '12px 0',
      horizontalMargin: '0 0 16px 0',
      inkBarColor: '#0070d2',
      itemColor: '#54698d',
      itemHoverColor: '#16325c',
      itemSelectedColor: '#0070d2',
      titleFontSize: 13,
      titleFontSizeLG: 14,
      titleFontSizeSM: 12,
    },

    // Breadcrumb - Navigation path
    Breadcrumb: {
      itemColor: '#54698d',
      lastItemColor: '#16325c',
      linkColor: '#0070d2',
      linkHoverColor: '#0062b3',
      separatorColor: '#b0b6bf',
      separatorMargin: 8,
      fontSize: 13,
      iconFontSize: 12,
    },

    // Statistic - KPI display
    Statistic: {
      titleFontSize: 12,
      contentFontSize: 28,
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    },

    // Progress - Status bars
    Progress: {
      defaultColor: '#0070d2',
      remainingColor: '#e5e8ed',
      circleTextFontSize: '1em',
      lineBorderRadius: 100,
    },

    // Descriptions - Detail panels
    Descriptions: {
      labelBg: '#f9fafb',
      contentColor: '#16325c',
      titleColor: '#16325c',
      titleMarginBottom: 16,
      itemPaddingBottom: 12,
      colonMarginRight: 8,
      colonMarginLeft: 2,
      extraColor: '#54698d',
    },

    // Form - Data entry
    Form: {
      labelColor: '#16325c',
      labelFontSize: 13,
      labelHeight: 32,
      labelColonMarginInlineEnd: 8,
      labelColonMarginInlineStart: 2,
      itemMarginBottom: 20,
      verticalLabelPadding: '0 0 6px',
      verticalLabelMargin: 0,
    },

    // Modal - Dialog windows
    Modal: {
      headerBg: '#ffffff',
      contentBg: '#ffffff',
      footerBg: '#f9fafb',
      titleFontSize: 16,
      titleLineHeight: 1.5,
      titleColor: '#16325c',
    },

    // Drawer - Side panels
    Drawer: {
      footerPaddingBlock: 12,
      footerPaddingInline: 16,
    },

    // Alert - System messages
    Alert: {
      defaultPadding: '12px 16px',
      withDescriptionIconSize: 20,
      withDescriptionPadding: '16px 20px',
    },

    // Message - Toast notifications
    Message: {
      contentBg: '#ffffff',
      contentPadding: '10px 16px',
    },

    // Notification - System alerts
    Notification: {
      width: 384,
      padding: 20,
    },

    // Tree - Hierarchical data
    Tree: {
      titleHeight: 28,
      nodeHoverBg: '#f5f7fa',
      nodeSelectedBg: '#e8f4fd',
      directoryNodeSelectedBg: '#e8f4fd',
      directoryNodeSelectedColor: '#0070d2',
    },

    // Timeline - Activity history
    Timeline: {
      itemPaddingBottom: 20,
      dotBorderWidth: 2,
      dotBg: '#ffffff',
      tailColor: '#d8dde6',
      tailWidth: 2,
    },

    // Steps - Process workflow
    Steps: {
      iconSize: 28,
      iconSizeSM: 24,
      iconFontSize: 13,
      titleLineHeight: 1.5,
      customIconSize: 28,
      customIconFontSize: 20,
      descriptionMaxWidth: 160,
      dotSize: 8,
      dotCurrentSize: 10,
    },
  },
};

// Dark theme variant for enterprise
const enterpriseDarkTheme = {
  token: {
    ...enterpriseTheme.token,
    // Dark mode colors
    colorBgContainer: '#1e2a3a',
    colorBgElevated: '#243447',
    colorBgLayout: '#0d1b2a',
    colorBgSpotlight: '#1e2a3a',

    colorBorder: '#3d4f61',
    colorBorderSecondary: '#2d3f51',

    colorText: '#e8ecf0',
    colorTextSecondary: '#9aa8b8',
    colorTextTertiary: '#7a8a9a',
    colorTextQuaternary: '#5a6a7a',

    colorPrimary: '#3d9df6',
    colorInfo: '#3d9df6',
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#ff4d4f',

    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
    boxShadowSecondary: '0 4px 12px rgba(0, 0, 0, 0.4)',
    boxShadowTertiary: '0 1px 2px rgba(0, 0, 0, 0.2)',
  },
  components: {
    ...enterpriseTheme.components,
    Layout: {
      ...enterpriseTheme.components.Layout,
      headerBg: '#0d1b2a',
      siderBg: '#0d1b2a',
      bodyBg: '#0d1b2a',
      footerBg: '#0d1b2a',
      triggerBg: '#16325c',
    },
    Table: {
      ...enterpriseTheme.components.Table,
      headerBg: '#1e2a3a',
      headerColor: '#e8ecf0',
      rowHoverBg: '#243447',
      rowSelectedBg: '#1a3d5c',
      rowSelectedHoverBg: '#214a6d',
      footerBg: '#1e2a3a',
      footerColor: '#e8ecf0',
      borderColor: '#3d4f61',
    },
    Card: {
      ...enterpriseTheme.components.Card,
      headerBg: '#1e2a3a',
      actionsBg: '#1a2535',
    },
    Button: {
      ...enterpriseTheme.components.Button,
      defaultBg: '#1e2a3a',
      defaultBorderColor: '#3d4f61',
      defaultColor: '#e8ecf0',
      defaultHoverBg: '#243447',
      defaultHoverBorderColor: '#5a6a7a',
      defaultHoverColor: '#e8ecf0',
      defaultActiveBg: '#2d3f51',
      defaultActiveBorderColor: '#7a8a9a',
      defaultActiveColor: '#e8ecf0',
      textHoverBg: 'rgba(255, 255, 255, 0.08)',
    },
    Input: {
      ...enterpriseTheme.components.Input,
      activeBg: '#1e2a3a',
      hoverBg: '#1e2a3a',
      activeBorderColor: '#3d9df6',
      hoverBorderColor: '#5a6a7a',
      activeShadow: '0 0 0 2px rgba(61, 157, 246, 0.2)',
    },
    Select: {
      ...enterpriseTheme.components.Select,
      controlItemBgActive: '#1a3d5c',
      controlItemBgHover: '#243447',
      optionActiveBg: '#1a3d5c',
      optionSelectedBg: '#1a3d5c',
    },
    Tag: {
      ...enterpriseTheme.components.Tag,
      defaultBg: '#2d3f51',
      defaultColor: '#e8ecf0',
    },
    Tabs: {
      ...enterpriseTheme.components.Tabs,
      cardBg: '#1e2a3a',
      inkBarColor: '#3d9df6',
      itemColor: '#9aa8b8',
      itemHoverColor: '#e8ecf0',
      itemSelectedColor: '#3d9df6',
    },
    Modal: {
      ...enterpriseTheme.components.Modal,
      headerBg: '#1e2a3a',
      contentBg: '#1e2a3a',
      footerBg: '#1a2535',
      titleColor: '#e8ecf0',
    },
    Descriptions: {
      ...enterpriseTheme.components.Descriptions,
      labelBg: '#1a2535',
      contentColor: '#e8ecf0',
      titleColor: '#e8ecf0',
    },
    Form: {
      ...enterpriseTheme.components.Form,
      labelColor: '#e8ecf0',
    },
    Tree: {
      ...enterpriseTheme.components.Tree,
      nodeHoverBg: '#243447',
      nodeSelectedBg: '#1a3d5c',
      directoryNodeSelectedBg: '#1a3d5c',
      directoryNodeSelectedColor: '#3d9df6',
    },
    Timeline: {
      ...enterpriseTheme.components.Timeline,
      dotBg: '#1e2a3a',
      tailColor: '#3d4f61',
    },
  },
};

export { enterpriseTheme, enterpriseDarkTheme };
export default enterpriseTheme;
